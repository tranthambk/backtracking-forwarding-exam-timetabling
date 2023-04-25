import pandas as pd
from ast import literal_eval
import json
from itertools import product
from typing import *
import numpy as np

#     json_data = json.dumps(dict_data)
#     with open("data/data.json", "w") as json_file:
#         json_file.write(json_data)




def get_attr(x, name_atrr = "@id"):
    try:
        ls_val = [x[idx][name_atrr] for idx in range(len(x))]
        return ls_val
    except Exception as e:
        return []
def parse_room_period(data: dict) -> pd.DataFrame:
    """Parse Relationship of room and period"""
    ls_dict_room = data["examtt"]["rooms"]["room"]
    df = pd.DataFrame(ls_dict_room)

    df["period_id"] = df["period"].apply(lambda x: get_attr(x))
    df =  df.explode("period_id")
    df.rename(columns = {"@id": "room_id"}, inplace = True)
    df = df[["room_id", "period_id"]]
    return df


def parse_exam(data: dict, ls_room_period: List[Tuple[str, str]]) -> pd.DataFrame:
    """Parse exam info from dictionary data"""

    ls_dict_exam = data["examtt"]["exams"]["exam"]
    
    df = pd.DataFrame(ls_dict_exam)

    df["ls_period"] = df["period"].apply(lambda x: get_attr(x))
    df["ls_room"] = df["room"].apply(lambda x: get_attr(x))
    df["ls_pair"] = df.apply(lambda x: [ str(i[0])+":"+str(i[1]) for i in  list(product(x["ls_room"], x["ls_period"]))], axis = 1)
    df["ls_room_period_valid"] = df["ls_pair"].apply(lambda x: np.intersect1d(x, ls_room_period))
    return df

def parse_student_exam(data: dict):
    """Parse student and exam id that student joined from dictionary data"""
  
    ls_dict_student = data["examtt"]["students"]["student"]
    df = pd.DataFrame(ls_dict_student)

    df["exam_id"] = df["exam"].apply(lambda x: get_attr(x))
    df =  df.explode("exam_id")
    df.rename(columns = {"@id": "student_id"}, inplace = True)
    df = df[["student_id", "exam_id"]]
    return df

def get_metadata_period(data: dict) -> pd.DataFrame:
    """Parse meta data of period from dictionary data"""
  
    ls_dict_period = data["examtt"]["periods"]["period"]
    df = pd.DataFrame(ls_dict_period)
    df.rename(columns = {"@id": "period_id", "@length": "length",\
                         "@day": "day", "@time": "time"}, 
            inplace = True)
    df.drop(columns = ["@penalty"], inplace = True)
    return df


# path_file = "data/pu-exam-fal12.xml"
# with open(path_file) as file:
#     data = xmltodict.parse(file.read())

# df_meta_period = get_metadata_period(data)
# print(df_meta_period)
# df_student_exam =  parse_student_exam(data)
# print(df_student_exam)
# df_room_period: pd.DataFrame = parse_room_period(data)
# print(df_room_period)

# ls_room_period_constraint: List = list(df_room_period.apply(lambda x: str(x["room_id"])+":"+str(x["period_id"]), axis = 1))
# df_exam: pd.DataFrame = parse_exam(data, ls_room_period_constraint)
# print(df_exam)
# df_meta_period.to_csv("data/metadata_period.csv", index = False)

# df_student_exam.to_csv("data/student_exam.csv", index = False)

# df_room_period.to_csv("data/room_period.csv", index = False)
# df_exam.to_csv("data/exam.csv", index = False)




# print(pd.DataFrame()
# print(pd.DataFrame(dict_data["examtt"]["periods"]))
# print(pd.DataFrame(dict_data["examtt"]["rooms"]["room"]))
# print(pd.DataFrame(dict_data["examtt"]["exams"]["exam"]))
# print(pd.DataFrame(dict_data["examtt"]["students"]["student"]))
# print(pd.DataFrame(dict_data["examtt"]["instructors"]["instructor"]))
# print(pd.DataFrame(dict_data["examtt"]["constraints"]))
