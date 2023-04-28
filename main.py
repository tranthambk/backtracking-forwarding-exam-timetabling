
from BC_FC import *
from data_parser import *

if __name__ == "__main__":
    path = "data/data.xlsx"
    df_meta_period, df_student_exam, df_exam, df_room_period = parse_from_excel(path)
    ls_dict_exam = df_exam.to_dict("records")

    t_0 = time.time()
    exam_timetabling = ExamTimetabling(ls_dict_exam[:50], df_meta_period, df_student_exam)
    a = exam_timetabling.find_schedule()
    print(exam_timetabling)
    print("TOTAL TIME: ", time.time() -  t_0)

