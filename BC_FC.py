
import time
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
  def __init__(self, ls_dict_exam, df_meta_period: pd.DataFrame):
    self.ls_dict_exam = ls_dict_exam
    self.df_meta_period = df_meta_period
  
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
          id_period =  assignment[0].split(":")[1]
          id_room =  assignment[0].split(":")[0]
          day  = self.df_meta_period[self.df_meta_period.period_id == id_period]["day"].iloc[0]
          time_exam  = self.df_meta_period[self.df_meta_period.period_id == id_period]["time"].iloc[0]
          schedule_ll.append([str(exam),day, time_exam,  str(id_room), str(id_period)])
        except Exception as e:
          print(e)
          continue
      
    df = pd.DataFrame(schedule_ll, columns=['Exam ID',  "Date", "time", 'Room', 'Period'])
    # df.sort_values('time', inplace=True)
    return df
  def __str__(self):
    if self._scheduled:
        return format_for_print(self._schedule_df)
    else:
        return "Unscheduled timetable"