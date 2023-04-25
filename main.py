
import xmltodict
from BC_FC import *
from data_parser import *

if __name__ == "__main__":
    

    path_file = "data/pu-exam-fal12.xml"
    with open(path_file) as file:
        data = xmltodict.parse(file.read())

    df_meta_period = get_metadata_period(data)
    print(df_meta_period)
    df_student_exam =  parse_student_exam(data)
    print(df_student_exam)
    df_room_period: pd.DataFrame = parse_room_period(data)
    print(df_room_period)

    ls_room_period_constraint: List = list(df_room_period.apply(lambda x: str(x["room_id"])+":"+str(x["period_id"]), axis = 1))
    df_exam: pd.DataFrame = parse_exam(data, ls_room_period_constraint)
    print(df_exam)

    df_exam = df_exam[["@id", "ls_room_period_valid"]].rename(columns = {"@id": "id"})
    ls_dict_exam = df_exam.to_dict("records")

    t_0 = time.time()
    print("NUM EXAM: ", len(ls_dict_exam))
    exam_timetabling = ExamTimetabling(ls_dict_exam[:500], df_meta_period)
    a = exam_timetabling.find_schedule()
    print(exam_timetabling)
    print("TOTAL TIME: ", time.time() -  t_0)

