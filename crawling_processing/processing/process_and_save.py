# 학과별 강의 csv 파일을 메인 로직(filtering, making)에서 사용하기 편하게 가공하는 모듈

import pandas as pd

from processing.constant_variable import *
from processing.module.import_csv import *
from processing.module.entire_course import *
from processing.module.convert_time_classroom import *
from processing.module.course_by_time import *
from processing.module.course_by_department import *


# [import_csv 모듈] 학과 강의 및 커리큘럼 csv 파일 생성
# input: "course" 또는 "curriculum"
# output: 학과별 강의 or 커리큘럼이 담긴 DataFrame list
# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수 가져오기
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

def import_csv_module(data_type):
    print("import_csv_module started.")
    
    if data_type == "course":
        prefix = "raw_data/lecture_data/"
    elif data_type == "curriculum":
        prefix = "raw_data/processed_curriculum/"
    else:
        raise ValueError("타입 입력이 잘못되었습니다. 'course' 또는 'curriculum'을 입력해주세요.")
    
    bucket = AWS_BUCKET_NAME  # S3 버킷 이름
    department_name_to_id, department_id_to_name, df_list = import_routine(bucket, prefix)

    department_name_to_id_df = pd.DataFrame.from_dict(
        department_name_to_id, orient="index", columns=["id"]
    )
    department_id_to_name_df = pd.DataFrame(
        department_id_to_name, columns=["department"]
    )

    department_name_to_id_df.to_csv(
        f"{PROCESSED_DEPARTMENT_INDEX_PATH}/department_name_to_id_for_{data_type}.csv"
    )
    department_id_to_name_df.to_csv(
        f"{PROCESSED_DEPARTMENT_INDEX_PATH}/department_id_to_name_for_{data_type}.csv"
    )

    for department_id, df in enumerate(df_list):
        department_name = department_id_to_name[department_id]
        df.to_csv(f"{PROCESSED_IMPORT_PATH}/{data_type}/{department_name}.csv")
    '''
    print(department_name_to_id)
    print(department_id_to_name)
    print(df_list[department_name_to_id["컴퓨터공학과-컴퓨터공학"]])
    print("import_csv_module 출력 끝.")
    '''
    print("import_csv_module finished.")
    
    return department_name_to_id, department_id_to_name, df_list



# [add_rating 모듈] 강의 평점을 추가한 csv 파일 생성
# input: 학과별 강의 DataFrame list
# output: 강의 평점이 추가된 DataFrame list
def add_rating_module(df_course_list):
    print("add_rating_module started.")
    # S3 버킷과 경로 설정
    bucket = os.getenv('AWS_BUCKET_NAME')
    key = 'raw_data/review.csv'  # S3 내의 review.csv 파일 경로

    # S3에서 review.csv 파일 읽기
    df_review = read_csv_from_s3(bucket, key)
    df_review.drop(columns=["review"], inplace=True)
    
    print("add_rating_module finished.")

    return list(
        map(
            lambda df_course: pd.merge(
                df_course, df_review, on=["course_name", "professor"], how="left"
            ),
            df_course_list,
        )
    )


# [entire_course 모듈] 전체 & 교양선택 강의 csv 파일 생성
# input: 학과별 강의 DataFrame list
# output: 전체 & 교양선택 강의 DataFrame
def entire_course_module(df_course_list, department_id_to_name_for_course):
    print("entire_course_module started.")
    
    entire_course_df = get_entire_course_df(
        df_course_list, department_id_to_name_for_course
    )
    elective_course_df = get_elective_course_df(entire_course_df)

    entire_course_df.to_csv(f"{PROCESSED_ENTIRE_COURSE_PATH}/entire_course.csv")
    elective_course_df.to_csv(f"{PROCESSED_ENTIRE_COURSE_PATH}/elective_course.csv")
    '''
    # 출력 테스트 코드
    print(entire_course_df)
    print(elective_course_df)
    print("entire_course_module 출력 끝.")
    '''
    print("entire_course_module finished.")
    
    return entire_course_df, elective_course_df


# [time_str_to_bit 모듈] DataFrame 내부의 string 형태의 시간을 bit ndarray로 변환한 csv 파일 생성
# input: 전체 & 교양선택 강의 DataFrame
# output: 시간이 bit ndarray로 변환된 DataFrame
def convert_time_classroom(entire_course_df, elective_course_df, column_name):
    print("convert_time_classroom started.")
    entire_course_bit_df = convert_time_classroom_df(entire_course_df, column_name)
    elective_course_bit_df = convert_time_classroom_df(elective_course_df, column_name)

    entire_course_bit_df.to_csv(
        f"{PROCESSED_TIME_STR_TO_BIT_PATH}/entire_course_bit.csv"
    )
    elective_course_bit_df.to_csv(
        f"{PROCESSED_TIME_STR_TO_BIT_PATH}/elective_course_bit.csv"
    )
    '''
    # 출력 테스트 코드
    print(entire_course_bit_df)
    print(elective_course_bit_df)
    print("time_str_to_bit_module 출력 끝.")
    '''
    print("convert_time_classroom finished.")
    
    return entire_course_bit_df, elective_course_bit_df


# [course_by_time 모듈] 특정 시간 강의의 csv 파일 생성
# input: 시간이 bit ndarray로 변환된 DataFrame
# output: None
def course_by_time_module(course_bit_df):
    print("course_by_time_module started.")
    
    course_by_all_time = get_course_by_all_time(course_bit_df)

    for day_index, day_df_list in enumerate(course_by_all_time):
        for time_index, time_df in enumerate(day_df_list):
            time_df.to_csv(
                f"{PROCESSED_COURSE_BY_TIME_PATH}/{day_index}_{time_index}.csv"
            )
    '''
    # 출력 테스트 코드
    print(course_by_all_time[3][10])
    print("course_by_time_module 출력 끝.")
    '''
    print("course_by_time_module finished.")

# [course_by_department 모듈] 각 학과가 들어야하는 강의를 교양, 전공으로 분류한 csv 파일 생성
# input: 학과별 강의 DataFrame list
#        전체 강의 DataFrame (시간이 bit ndarray로 변환된 DataFrame)
#        커리큘럼에 있는 학과의 id -> 학과이름 변환 list
#        강의시간표에 있는 학과의 학과이름 -> id 변환 dict
# output: None
def course_by_department_module(
    df_course_list,
    entire_course_bit_df,
    department_id_to_name_for_curriculum,
    department_name_to_id_for_course,
):
    print("course_by_department_module started.")
    # 커리큘럼에 있는 학과를 토대로 DataFrame을 생성
    department_possible_df_list = create_empty_department_possible_df(
        department_id_to_name_for_curriculum
    )
    # 학과 이름이 df_course_list에 있으면, 해당 강의를 전공과 교양필수로 나누어 DataFrame에 추가
    department_possible_df_list = add_include_course_to_department_possible_df(
        df_course_list,
        entire_course_bit_df,
        department_possible_df_list,
        department_id_to_name_for_curriculum,
        department_name_to_id_for_course,
    )

    # 학과별 대학교교양필수(GEB) 과목을 교양필수 DataFrame에 추가
    add_geb_to_department_possible_df(
        entire_course_bit_df,
        df_curriculum_list,
        department_possible_df_list,
        department_id_to_name_for_curriculum,
    )

    # 학과별 핵심교양(GED) 과목을 교양필수 DataFrame에 추가
    add_ged_to_department_possible_df(
        entire_course_bit_df,
        df_curriculum_list,
        department_possible_df_list,
        department_id_to_name_for_curriculum,
    )

    # csv 파일로 저장
    for department_id, department_name in enumerate(
        department_id_to_name_for_curriculum
    ):
        department_possible_df_list[department_id][0].to_csv(
            f"{PROCESSED_COURSE_BY_DEPARTMENT_PATH}/{department_name}_major.csv"
        )
        department_possible_df_list[department_id][1].to_csv(
            f"{PROCESSED_COURSE_BY_DEPARTMENT_PATH}/{department_name}_liberal_required.csv"
        )
    '''
    # 출력 테스트 코드
    print(
        department_possible_df_list[
            department_name_to_id_for_curriculum["컴퓨터공학과-컴퓨터공학"]
        ]
    )
    print("course_by_department_module 출력 끝.")
    '''
    print("course_by_department_module finished.")

# main 함수
#if __name__ == "__main__":
def process_all():
    # csv 파일을 불러와 사용할 변수로 저장
    print("Processing started.")
    global department_name_to_id, department_id_to_name, df_list, df_course_list, department_name_to_id_for_course, df_curriculum_list, department_name_to_id_for_curriculum, department_id_to_name_for_curriculum
    for data_type in ["course", "curriculum"]:
        department_name_to_id, department_id_to_name, df_list = import_csv_module(
            data_type
        )

        if data_type == "course":
            df_course_list = df_list
            department_name_to_id_for_course = department_name_to_id
            department_id_to_name_for_course = department_id_to_name
        elif data_type == "curriculum":
            df_curriculum_list = df_list
            department_name_to_id_for_curriculum= department_name_to_id
            department_id_to_name_for_curriculum = department_id_to_name

    global entire_course_df, elective_course_df, entire_course_bit_df, elective_course_bit_df, department_possible_df_list
    # 모듈 실행
    df_course_list = add_rating_module(df_course_list)
    entire_course_df, elective_course_df = entire_course_module(
        df_course_list, department_id_to_name_for_course
    )
    entire_course_bit_df, elective_course_bit_df = convert_time_classroom(
        entire_course_df, elective_course_df, "time_classroom"
    )
    course_by_time_module(entire_course_bit_df)

    department_possible_df_list = course_by_department_module(
        df_course_list,
        entire_course_bit_df,
        department_id_to_name_for_curriculum,
        department_name_to_id_for_course,
    )
    print("Processing finished.")
