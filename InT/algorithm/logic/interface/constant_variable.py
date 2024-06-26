# 파일 저장 경로
RESOURCE_PATH = "algorithm/resource"
PROCESSED_PATH = f"{RESOURCE_PATH}/processed"
PROCESSED_DEPARTMENT_INDEX_PATH = f"{PROCESSED_PATH}/department_index"
PROCESSED_IMPORT_PATH = f"{PROCESSED_PATH}/import_csv"
PROCESSED_ENTIRE_COURSE_PATH = f"{PROCESSED_PATH}/entire_course"
PROCESSED_TIME_STR_TO_BIT_PATH = f"{PROCESSED_PATH}/time_str_to_bit"
PROCESSED_COURSE_BY_TIME_PATH = f"{PROCESSED_PATH}/course_by_time"
PROCESSED_COURSE_BY_DEPARTMENT_PATH = f"{PROCESSED_PATH}/course_by_department"

# 요일, 교시
DAY_NUM = 7
TIME_NUM = 31

# user taste
AMPM = 0
TIME1 = 1
SPACE = 2
AM = True
PM = False
SPACE_TRUE = True
SPACE_FALSE = False

# filter type
AVOID_TIME = 0
PREFER_PROFESSOR = 1
AVOID_PROFESSOR = 2

# convert mode
TO_FRONT = 0
TO_BACK = 1

# opject type
TIMETABLE = 0
COURSE = 1
COURSE_EXTENDED = 2
PROFESSOR = 3
FILTER = 4
MODE = 5

# sort mode
SQAURE_AREA = 0
TASTE = 1