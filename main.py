def parse_room_period(doc):
  t_0 = time.time()
  rooms = doc.getElementsByTagName("rooms")
  ls_room = rooms[0].getElementsByTagName("room")
  ls_room_period= []
  for room in ls_room:
    id_room = room.getAttribute("id")
    for period in room.getElementsByTagName("period"):
      ls_room_period.append((id_room, period.getAttribute("id")))
  total_time_1 = time.time() - t_0
  print(total_time_1)
  return ls_room_period
def parse_student_exam(doc):
  
  ls_exams = doc.getElementsByTagName("exams")[0].getElementsByTagName("exam")
  ls_students = doc.getElementsByTagName("students")[0].getElementsByTagName("student")
  ls_pair_student_exam = []
  for student in ls_students:
    id_stu = student.getAttribute("id")
    ls_exam_id = [i.getAttribute("id") for i in student.getElementsByTagName("exam")]
    for id_exam in ls_exam_id:
      ls_pair_student_exam.append((id_exam, id_stu))
  return ls_pair_student_exam, ls_exams, ls_students

def parse_exam(ls_exam):

  t_0 =time.time()
  ls_dict_exam = []
  for exam in ls_exams:
    try:
      id_exam = exam.getAttribute("id")
      ls_period = [i.getAttribute("id") for i in exam.getElementsByTagName("period")]
      ls_room = [i.getAttribute("id") for i in exam.getElementsByTagName("room")]
      
      ls_pair = list(product(ls_room, ls_period))
      ls_period_valid = [value for value in ls_pair if value in ls_room_period]
      dict_exam = {"id": id_exam, \
                      "ls_period": ls_period,
                      "ls_room": ls_room,
                      "ls_room_period_valid": ls_period_valid,
                      "ls_student": list(df[df.id_exam == id_exam]["id_student"].values)
                      }
      ls_dict_exam.append(dict_exam)
    except Exception as e:
      print(e)
      continue
  print("TOTAL TIME: ",  time.time() - t_0)

  return ls_dict_exam
def get_metadata_room(doc):
  rooms = doc.getElementsByTagName("periods")
  ls_room = rooms[0].getElementsByTagName("period")
  ls_meta_period= []
  for room in ls_room:
    id_room = room.getAttribute("id")
    day = room.getAttribute("day")
    time = room.getAttribute("time")
    ls_meta_period.append((id_room, day, time))
  return ls_meta_period

import time
import xml.dom.minidom
from itertools import product
import pandas as pd 

from copy import deepcopy
import time
# output_schedule = {
#     "1": [("1", "3")],
#     "2": [("2", "3")],
# }


"""
Some helper functions used throughout the scheduler.
"""
from collections import OrderedDict
from prettytable import PrettyTable
    
    
def format_for_print(df):
    """Print dataframe as pretty table."""  
    table = PrettyTable(list(df.columns))
    
    for row in df.itertuples():
        table.add_row(row[1:])
    return str(table)


def sort_dict_by_mrv(d):
    """Sort dictionary according to minimun remaining values heuristic."""
    return OrderedDict(sorted(d.items(), key=lambda x: len(x[1]) if isinstance(x[1], set) else 0))

def get_first_element(iterable):
    
    return next(iter(iterable))

 



"""Custom exeptions."""
class ImpossibleAssignments(ValueError):
    
    pass
class ExamTimetabling:
  def __init__(self, ls_dict_exam):
    self.ls_dict_exam = ls_dict_exam
  
  def find_schedule(self):
      """Schedule the timetable."""
      # Use a dictionary to map an assignment to each lecture.
      schedule = self.init_schedule()
      try:
          final_schedule = self._assign_values(schedule)
          self._scheduled = True
          self._schedule = final_schedule
          self._schedule_df = self._save_schedule_in_dataframe()
          return final_schedule
      except ImpossibleAssignments:
          raise ImpossibleAssignments( 'Unable to find schedule without violating constraints.' )
  def init_schedule(self):
    """
      Initialize schedule where each lecture is mapped to all possible assignments.
    """
    schedule = {}
    for exam in self.ls_dict_exam:
      schedule[exam["id"]] = set(exam["ls_room_period_valid"])
    return schedule
  def _schedule_complete(self, schedule):
  #   """Check whether there are still unassigned variables in the schedule."""
    
    for assignment in schedule.values():
        if len(assignment) > 1:
            return False
    return True
  def _assign_values(self, schedule):
      """
      Assign an unassigned variable and traverse the search tree further.
      
      Args:
          schedule (dict): The partially constructed schedule.
          assignable (set): The values that have not yet been assigned.
      """
      # base case 
      if self._schedule_complete(schedule):
          return schedule

      schedule = deepcopy(schedule)
      
      # Iterate over unassigned variables.
      ls_unassign = self._get_unassigned_vars(schedule, sort=True)
      for exam in ls_unassign:
          # Iterate over domain.
          domain = deepcopy(schedule[exam])
          for assignment in domain:
              schedule[exam] = [assignment]
      #         # Propagate constraints.
              try:
                  reduced_domains_schedule = self._reduce_domains(exam,deepcopy(schedule), assignment)
                  # reduced_domains_schedule = self._resolve_small_domains(reduced_domains_schedule)
                  # Recursively call the function to traverse the search tree.
                  return self._assign_values(reduced_domains_schedule)
              except ImpossibleAssignments:
                  # Remove invalid assignment and restore domain if higher order constraints cause 
                  # domain to become empty.
                  schedule[exam] = domain
                  continue

  def _get_unassigned_vars(self, schedule, sort=False):

     """Get all variables that have not yet been assigned a value."""
     unassigned_exam = []
      
     for exam, domain_value in schedule.items():
       if len(domain_value) > 1:
         unassigned_exam.append(exam)
     return unassigned_exam
  def _reduce_domains(self, exam_old, schedule, new_assignment):
        """Reduce domains by propagating constraints.""" 
        
        for exam in self._get_unassigned_vars(schedule):
            # Remove the newly assigned value from any other domain.
            if new_assignment in schedule[exam]:
              schedule[exam].remove(new_assignment)

            # Check whether the removal makes the domain empty.
            if not schedule[exam]:
                raise ImpossibleAssignments('Assignment leads to inconsistencies.')     
        return schedule
  def _save_schedule_in_dataframe(self):
    """Save the schedule dictionary to a pandas dataframe."""
    schedule_ll = []
    for exam, assignment in self._schedule.items():
        try:
          day  = df_meta_period[df_meta_period.exam_id == assignment[0][1]]["day"].iloc[0]
          time_exam  = df_meta_period[df_meta_period.exam_id == assignment[0][1]]["time"].iloc[0]
          schedule_ll.append([str(exam),day, time_exam,  str(assignment[0][0]), str(str(assignment[0][1]))])
        except Exception as e:
          continue
    df = pd.DataFrame(schedule_ll, columns=['Exam ID',  "Date", "time", 'Room', 'Period'])
    # df.sort_values('time', inplace=True)
    return df
  def __str__(self):
    if self._scheduled:
        return format_for_print(self._schedule_df)
    else:
        return "Unscheduled timetable"

if __name__ == "__main__":
    


    path_data_exam = "data/pu-exam-fal12.xml"
    doc = xml.dom.minidom.parse(path_data_exam)
    ls_room_period = parse_room_period(doc)
    ls_pair_student_exam, ls_exams, ls_students = parse_student_exam(doc)
    df = pd.DataFrame(ls_pair_student_exam, columns = ["id_exam", "id_student"])

    ls_dict_exam = parse_exam(ls_exams)
    ls_meta_period = get_metadata_room(doc)

    df_meta_period = pd.DataFrame(ls_meta_period, columns = ["exam_id", "day", "time"])
    df_pair_stu_exam = pd.DataFrame(ls_pair_student_exam, columns = ["id_exam", "id_student"])

    DF_DICT_EXAM = pd.DataFrame(ls_dict_exam)

    df_room_period = pd.DataFrame(ls_room_period, columns = ["id_room", "id_period"])





    t_0 = time.time()
    print("NUM EXAM: ", len(ls_dict_exam))
    exam_timetabling = ExamTimetabling(ls_dict_exam)
    exam_timetabling.find_schedule()
    print(exam_timetabling)
    print("TOTAL TIME: ", time.time() -  t_0)

