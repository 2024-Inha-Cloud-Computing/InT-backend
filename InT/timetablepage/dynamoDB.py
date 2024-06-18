import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import os
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from decimal import Decimal
import json

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# SubTimetables
# timetable 1개를 만들기 위한 강의 추가
# favorite, homepage 용
class SubTimetables:
    def __init__(self):
        self.favorite_timetable = []
    
    def add_course(self, course_id, day, duration, professor, room, subject, time):
        course = {
                "course_id": course_id,
                "day": day,
                "duration": Decimal(duration),
                "professor": professor,
                "room": room,
                "subject": subject,
                "time": Decimal(time)
            }
        self.favorite_timetable.append(course)
    
    def return_subtable(self):
        return self.favorite_timetable

# Timetables
# user_id, favorite, homepage를 하나 묶어서 DB에 저장
class Timetables:
    def return_timetable(self, user_id, timetable):
        return {
            "user_id": Decimal(user_id),
            "homepage_timetable": timetable
        }
        
# # Favorite_Timetable
# # 찜한 timetable들을 한 리스트에 추가
# class Favorite_Timetable:
#     def __init__(self):
#         self.favorite_timetable=[]
    
#     def add_favorite_timetable(self, timetables):
#         self.favorite_timetable.append(timetables.return_subtable())
    
#     def to_dynamodb_format(self):
#         return self.favorite_timetable


# def dynamo_to_python(dynamo_object: dict) -> dict:
#     deserializer = TypeDeserializer()
#     return {
#         k: deserializer.deserialize(v) 
#         for k, v in dynamo_object.items()
#     }  


# def convert_floats_to_decimals(obj):
#     if isinstance(obj, list):
#         return [convert_floats_to_decimals(item) for item in obj]
#     elif isinstance(obj, dict):
#         return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
#     elif isinstance(obj, float):
#         return Decimal(str(obj))
#     else:
#         return obj

# # python_json to dynamo_json
# def python_to_dynamo(python_object: dict) -> dict:
#     serializer = TypeSerializer()
#     python_object = convert_floats_to_decimals(python_object)
#     return {
#         k: serializer.serialize(v)
#         for k, v in python_object.items()
#     }
        
# 원래 데이터
data = {
    'homepage_timetable': [
        {
            'duration': Decimal('0'),
            'professor': '',
            'course_class_id': '',
            'color': '',
            'subject': '',
            'time': Decimal('0'),
            'day': '',
            'room': ''
        }
    ],
    'user_id': Decimal('0')
}

# Decimal 값을 float로 변환하는 함수
def convert_decimal_to_number(d):
    if isinstance(d, list):
        return [convert_decimal_to_number(i) for i in d]
    elif isinstance(d, dict):
        return {k: convert_decimal_to_number(v) for k, v in d.items()}
    elif isinstance(d, Decimal):
        return int(d) if d == data['user_id'] else float(d)
    else:
        return d
            
# Python에서 DynamoDB를 사용하는 클래스
# get, put, delete, update가 있다.
class DynamoDBModel:
    def __init__(self):
        self.table = boto3.resource(
            'dynamodb',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
            ).Table('int-dynamodb-cloudcomputing')
    
    
    
    # input: key (dictionary)
    # output: None or Value
    def get_item(self, key):
        try:
            res = self.table.get_item(Key=key)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        finally:
            print("get timetable")
        
        data = res.get('Item')
        data = convert_decimal_to_number(data)
        return data
        

    # input: item (dictionary)
    # output: 성공 1, 실패 0
    def put_item(self, item):
        try:
            res = self.table.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
        finally:
            print("put timetable")
            
        return res

    # input: key (dictionary)
    # output: 성공 1, 실패 0
    def delete_item(self, key):
        try:
            res = self.table.delete_item(Key=key)
        except ClientError as e:
            print(e)
        finally:
            print("delete timetable")
            
        return res