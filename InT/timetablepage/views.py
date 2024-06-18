from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from algorithm import *
from .dynamoDB import *
from algorithm.logic.interface.main import *
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from homepage.models import Users, AuthEmailTable, AuthPhoneTable
import ast
from .serializers import *
from .memoryDB import MemoryModel

# 모든 강의를 반환하는 API
# input : id
# output : ['~과, 과목, 학수번호', ...]
class AllCourseAPIView(APIView):
  def post(self, request):
    # input : id
    id = request.data.get("id")

    # DB 호출
    user = Users.objects.get(id=id)
    
    # TimetableInterface에 필요한 매개변수 생성    
    user_taste = [user.am_pm, user.first_class, user.space_time]
    
    # TimetableInterface 클래스 생성
    try:
        timetableInterface = TimetableInterface(user_taste)
    except:
      return Response({"courses":[]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 메모리에 클래스 저장
    MemoryModel.save(id, timetableInterface)
    
    # 모든 강의 데이터
    all_course_data = timetableInterface.search_course_routine("")
    
    print("\n")
    print("전체 데이터: ")
    print(all_course_data)
    
    return Response(
      {
        "courses":all_course_data
      },
      status=status.HTTP_200_OK
    )

# 검색창에서 검색 API
# input : 사용자가 입력한 단어 (학과명, 과목명, 학수번호), ID
# output : ['~과, 과목, 학수번호', ...]
class FindCourseAPIView(APIView):
  def post(self, request):
    # input : 검색창에 입력한 단어
    user_input = request.data.get("input")

    # DB 호출
    id = request.data.get("id")

    # 메모리에서 클래스 호출
    timetableInterface = MemoryModel.get(id)

    # search_course_routine 함수 호출
    all_course_data = timetableInterface.search_course_routine(f"{user_input}")
    
    # 변한 클래스값 메모리에 저장
    MemoryModel.save(id, timetableInterface)

    print("\n")
    print(f"입력값에 따른 데이터 : {user_input}")
    print(all_course_data)
    
    return Response({
      "courses":all_course_data 
      },
      status=status.HTTP_200_OK
    )

# 꼭 들어야하는 강의 API
# input : 꼭 들어야하는 강의들, ID, 성향 데이터를 가지고 있는 Class
# output : 들어야하는 강의들 조합
class FirstFilteringTimetableAPIView(APIView):
  def post(self, request):
    # input : 꼭 들어야하는 강의들, ID, 성향 데이터를 가지고 있는 Class
    courses =  ast.literal_eval(request.data.get("courses"))
    id = request.data.get("id")
    timetableInterface = MemoryModel.get(id)

    # require_course_timetable_routine 함수 호출
    react_courses = timetableInterface.require_course_timetable_routine(courses)
    
    # 변환된 클래스 저장
    MemoryModel.save(id, timetableInterface)
    
    print("\n")
    print("꼭 들어야하는 강의들 : ")
    print(courses)
    print("들어야하는 강의들을 조합 : ")
    print(react_courses)
    
    return Response({
        "courses": react_courses},
        status=status.HTTP_200_OK
    )

#
class SndFilLikeProfAPIView(APIView):
  def post(self, request):
    # 각 강의를 하시는 교수님을 알고 싶은 강의들
    courses =  ast.literal_eval(request.data.get("courses"))

    id = request.data.get("id")
    print(id)
    print("\n\n")
    
    timetableInterface = MemoryModel.get(id)
    print(type(timetableInterface))
    print("\n\n")
    react_professor = timetableInterface.find_professor_routine(courses)
    MemoryModel.save(id, timetableInterface)
    course_list = [{"id": index+1, "name": course, "professors": react_professor[course.split(',')[1][1:]]} for index, course in enumerate(courses)]

    return Response({
        "courses": course_list},
        status=status.HTTP_200_OK
    )

# 앞에 조건들로 시간표 만들기
# TODO : 준용이 오면 알고리즘 수정 후 해당 코드 고칠것.
class MakeTimeTableAPIView(APIView):
  def post(self, request):
    courses =  request.data.get("courses")
    id = request.data.get("id")
    avoid_time = request.data.get("time")
    avoid_professor = request.data.get("selectedHateProfessors")
    prefer_professor = request.data.get("selectedLikeProfessors")
    order = request.data.get("order")
    
    # 필요없는 코드
    # user = Users.objects.get(id=id)
    
    print(f"꼭 들어야하는 강의: {courses}\n")
    print(f"피해야하는 시간: {avoid_time}\n")
    print(f"각 강의 싫은 교수: {avoid_professor}\n")
    print(f"각 강의 좋은 교수: {prefer_professor}\n")
    print(f"각 순위: {order}\n\n")
    
    prefer_dict = {}
    avoid_dict = {}
    if prefer_professor != [] and prefer_professor != None:
      for prefer in prefer_professor:
        prefer_dict[prefer['course']] = prefer['professor']
    if avoid_professor !=[] and avoid_professor != None:
      for avoid in avoid_professor:
        avoid_dict[avoid['course']] = avoid['professor']
    
    print("형태를 바꿈: ")
    print(prefer_dict)
    print(avoid_dict)    
    print("\n\n")
    
    timetableInterface = MemoryModel.get(id)
    
    print("클래스 확인")
    print(timetableInterface)
    filter_data_front_object = [avoid_time, prefer_dict, avoid_dict]
    
    print("함수 입력값: ")
    print(filter_data_front_object)
      
    front_courses, flag = timetableInterface.timetable_filter_routine(filter_data_front_object, order)
    MemoryModel.save(id, timetableInterface)
    print("결과: ")
    print(front_courses)
    print(flag)
    
    return Response(
      {"courses": front_courses, 
      "flag": flag},
      status=status.HTTP_200_OK
      )



# timetable DB저장용으로 사용하는 API
class FirstFilteringDecideAPIView(APIView):
  def post(self, request):
    id = request.data.get("id")
    final = request.data.get("final")
    
    
    user = Users.objects.get(id = id)
    
    dynamoDB_timetable = Timetables()
    dynamoDB_input = dynamoDB_timetable.return_timetable(int(user.user_id), final)
    
    # 소수점 저장 안됨 so 바꿈.
    for item in dynamoDB_input['homepage_timetable']:
      item['time'] = int(item['time'] * 100)
      item['duration'] = int(item['duration'] * 100)
            
    print(dynamoDB_input)
    print("\n\n")
    
    try:
      dynamoDB = DynamoDBModel()
      dynamoDB.put_item(dynamoDB_input)
    except:
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
      return Response(status=status.HTTP_200_OK)
      
class DepartmentsAPIView(APIView):
  def post(self, request):
    timetableInterface = MemoryModel.get(id)
    department = timetableInterface.get_department_list_routine()
    print(department)
    return Response(
      {"department": department},
      status=status.HTTP_200_OK
      )
      
class GetScheduleAPIView(APIView):
  def post(self, request):
    liberal = request.data.get("liberal")
    major = request.data.get("major")
    id = request.data.get("id")
    user = Users.objects.get(id=id)
    
    timetableInterface = MemoryModel.get(id)

    print("\n")
    print(f"liberal: {liberal}")
    print(f"major: {major}")
    
    # 모드 list
    mode_list = liberal + major
    mode_list = [list(item.values()) for item in mode_list]
    for mode_element in mode_list:
      mode_element[0] = int(mode_element[0])
    
    print("\n")
    print("mode_list: ")
    print(mode_list)
    
    dynamoDB = DynamoDBModel()
    s3_courses = dynamoDB.get_item({"user_id":user.user_id})
    
    for item in s3_courses['homepage_timetable']:
        item['time'] = item['time'] / 100
        item['duration'] = item['duration'] / 100
    
    print("\n")
    print("S3_courses: ")
    print(s3_courses)
    
    courses = timetableInterface.auto_fill_routine(s3_courses['homepage_timetable'], mode_list)
    
    return Response(
      {"courses": courses},
      status=status.HTTP_200_OK
      )
      
class ManualAddManualAPIView(APIView):
  def post(self, request):
    # input : id
    id = request.data.get("id")

    user = Users.objects.get(id=id)

    timetableInterface = MemoryModel.get(id)
    
    all_course_data = timetableInterface.search_course_extended_routine(search_word="")
    
    print("\n")
    print("course 입력: ")
    print(all_course_data)
    
    department = timetableInterface.get_department_extended_list_routine()
    
    print("\n")
    print("department 입력: ")
    print(department)
    
    dynamoDB = DynamoDBModel()
    s3_courses = dynamoDB.get_item({"user_id":user.user_id})
    
    for item in s3_courses['homepage_timetable']:
        item['time'] = item['time'] / 100
        item['duration'] = item['duration'] / 100
        
    credits = timetableInterface.get_timetable_credit_routine(s3_courses['homepage_timetable'])
    
    print("\n")
    print("schedule 입력: ")
    print(s3_courses['homepage_timetable'])
    
    return Response({"schedule":s3_courses['homepage_timetable'], "course": all_course_data, "department":department, "credits":credits}, status=status.HTTP_200_OK)
    
    
class AddCourseAPIView(APIView):
  def post(self, request):
    id = request.data.get("id")
    course = request.data.get("course")
    
    user = Users.objects.get(id=id)
    
    dynamoDB = DynamoDBModel()
    s3_courses = dynamoDB.get_item({"user_id":user.user_id})
    
    
    
    timetableInterface = MemoryModel.get(id)
    
    schedule, credit = timetableInterface.add_course_in_timetable_routine(s3_courses['homepage_timetable'], course)
    
    if schedule == False:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    
    for item in schedule:
      item['time'] = int(item['time'] * 100)
      item['duration'] = int(item['duration'] * 100)
    
    s3_courses['homepage_timetable'] = s3_courses['homepage_timetable'] + schedule
    s3_courses['user_id'] = int(s3_courses['user_id'])
    
    for item in s3_courses['homepage_timetable']:
        item['time'] = int(item['time'])
        item['duration'] = int(item['duration'])
    
    print(s3_courses)
    
    dynamoDB.put_item(s3_courses)

    for item in s3_courses['homepage_timetable']:
        item['time'] = item['time'] / 100
        item['duration'] = item['duration'] / 100
    
    print("결과: ")
    print(credit)
    print(schedule)
    
    return Response({"schedule":schedule, "credits":str(credit)}, status=status.HTTP_200_OK)

class RemoveCourseAPIView(APIView):
  def post(self, request):
    id = request.data.get("id")
    course = request.data.get("courseName")
    
    user = Users.objects.get(id=id)
    
    dynamoDB = DynamoDBModel()
    s3_courses = dynamoDB.get_item({"user_id":user.user_id})
    
    for item in s3_courses['homepage_timetable']:
        item['time'] = item['time'] / 100
        item['duration'] = item['duration'] / 100
    
    timetableInterface = MemoryModel.get(id)
    
    print("입력값: ")
    print(s3_courses['homepage_timetable'])
    print(course)
    
    schedule, credit = timetableInterface.remove_course_in_timetable_routine(s3_courses['homepage_timetable'], course)
    
    print(schedule)
    
    for item in schedule:
      item['time'] = int(item['time'] * 100)
      item['duration'] = int(item['duration'] * 100)
    
    s3_courses['homepage_timetable'] = schedule
    s3_courses['user_id'] = int(s3_courses['user_id'])
    
    for item in s3_courses['homepage_timetable']:
        item['time'] = int(item['time'])
        item['duration'] = int(item['duration'])
    
    print(s3_courses)
    
    dynamoDB.put_item(s3_courses)

    for item in schedule:
        item['time'] = item['time'] / 100
        item['duration'] = item['duration'] / 100

    return Response({"schedule":schedule, "credits": credit}, status=status.HTTP_200_OK)

class ALLFindCourseAPIView(APIView):
  def post(self, request):
    id = request.data.get("id")
    input = request.data.get("input")
    
    timetableInterface = MemoryModel.get(id)
    course = timetableInterface.search_course_extended_routine(search_word=(input))
    print(course)
    return Response({"course":course}, status=status.HTTP_200_OK)
    
class FilteringCourseAPIView(APIView):
  def post(self, request):
    id = request.data.get("id")
    input = request.data.get("input")
    search = request.data.get("search")
    
    print("검색: ")
    print(input)
    print(type(input))
    print(search)
    print(type(search))
    
    algorithm_input = [input['department'], input['subjectType'], input['year'], input['credits']]
    print(algorithm_input)
    
    try:
      timetableInterface = MemoryModel.get(id)
      print(timetableInterface)
      course = timetableInterface.search_course_extended_routine(search_word=(search), filter_data=algorithm_input)
      print(course)
    except:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
      return Response({"course":course}, status=status.HTTP_200_OK)