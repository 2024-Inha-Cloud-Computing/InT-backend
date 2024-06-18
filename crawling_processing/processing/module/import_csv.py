import os
import unicodedata
import pandas as pd
import boto3
from io import BytesIO
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수 가져오기
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# S3 클라이언트 생성
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# S3에서 파일 목록 가져오기
def list_files_in_s3(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [content['Key'] for content in response.get('Contents', []) if content['Key'] != prefix]

# S3에서 파일 읽어오기
def read_csv_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(BytesIO(response['Body'].read()))

# csv 파일로부터 변환에 필요한 list & dict와 DataFrame list로 반환하는 함수
# input: s3 버킷 이름과 폴더 경로
# output: 학과별 [id <-> 학과명] list & dict, DataFrame list
def import_routine(bucket, prefix):
    # S3에서 csv 파일 목록 추출
    csv_files = list_files_in_s3(bucket, prefix)

    # 파일명을 같은 유니코드 인코딩(자소통합)으로 normalize
    csv_files = [unicodedata.normalize("NFC", x) for x in csv_files]

    # "학과"로 시작하는 파일명을 "기타"로 시작하는 파일명보다 앞서게 정렬
    csv_files.sort(key=sort_csv_file)

    return *get_department_dict(csv_files), import_csv(bucket, prefix, csv_files)

# csv 파일명에 따라 [id <-> 학과명] 간의 변환에 필요한 dict, list를 만드는 함수
# input: csv 파일명 list
# output: [id <-> 학과명] 간의 변환에 필요한 dict, list
def get_department_dict(csv_files):
    department_name_to_id = {}
    department_id_to_name = []

    # csv 파일명을 통해 학부과-전공명을 추출
    for file in enumerate(csv_files):
        # 확장자 제거 및 "/"와 "_"로 split
        file_name = file[1].split("/")[-1]
        file_remove_extension = file_name.split(".")[0]
        file_split = file_remove_extension.split("_")
        if file_split[0] == "기타":
            DEPARTMENT_NAME = "기타-" + file_split[1]

            department_name_to_id[DEPARTMENT_NAME] = file[0]
            department_id_to_name.append(DEPARTMENT_NAME)
        else:
            DEPARTMENT_NAME = file_split[1] + "-" + file_split[2]

            department_name_to_id[DEPARTMENT_NAME] = file[0]
            department_id_to_name.append(DEPARTMENT_NAME)

    return department_name_to_id, department_id_to_name

# 읽어온 csv 파일을 DataFrame의 list로 변환하는 함수
# input: s3 버킷 이름, 폴더 경로, csv 파일명 list
# output: DataFrame list
def import_csv(bucket, prefix, csv_files):
    df_list = []
    for file in csv_files:
        FILE_KEY = f"{file}"
        df = read_csv_from_s3(bucket, FILE_KEY)
        df_list.append(df)

    return df_list

# csv 파일 이름 정렬 key 함수
# input: csv 파일명
# output: 정렬 기준에 따른 우선순위 튜플
def sort_csv_file(file):
    file_name = file.split("/")[-1]
    file_remove_extension = file_name.split(".")[0]
    file_split = file_remove_extension.split("_")
    if file_split[0] == "기타":
        return (1, file)
    else:
        return (0, file)
