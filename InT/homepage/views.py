from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from .serializers import UsersSerializer
from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import permissions

from .ses import SNS_API
from .twilio import *

from .models import Users, AuthEmailTable, AuthPhoneTable
from timetablepage.dynamoDB import *
from django.db import connection

from django.utils import timezone
from datetime import date
import random

# login_view 로그인 버튼을 눌렀을 사용하는 API
class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Users.objects.get(id=username)
        except Exception:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            
            # TODO 성향에 들어갈 수 있도록 DB에서 유저가 첫 로그인 인지 확인
            #      첫 회원인 경우 response를 보내고 DB 수정
            if user.first_login == 0:
                Users.objects.filter(id=username).update(first_login=1)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "name": user.name,
                    "first_login": user.first_login,
                    "id": user.id,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


# 구독 이메일 보내기
# TODO : SNS는 구독확인 필요하다. 1. 다른 서비스를 연계해서 쓰거나 2. 사용자가 이메일 구독확인을 해야한다.
class AuthCheckAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is none"}, status=status.HTTP_400_BAD_REQUEST)

        sns_api = SNS_API()
        # 구독 가입 엔드포인트
        arn = sns_api.subscribe_by_email(email)
    
        try:
            data=AuthEmailTable.objects.get(email=email)
        except: # email이 없으면 생성성
            AuthEmailTable.objects.create(email=email, arn=arn)
        else:   # SNS에 구독 대기중이 사라진 경우 update 필요
            AuthEmailTable.objects.filter(email=data.email).update(arn=arn)
        
        return Response(status=status.HTTP_200_OK)

# 구독 확인
# 이메일 인증 확인
class AuthCheckInDBAPIView(APIView):
    def post(self, request):
        print("Hey!")
        auth = request.data.get("number")   # 해당코드는 필요없음.
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email or Auth Number is none"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=AuthEmailTable.objects.get(email=email)
        except:
            return Response({"error": "There is no email in DB"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            sns_api = SNS_API()
            if sns_api.check_subscribe_by_email(data.arn):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"error":"Please Check Your Email Or No ARN In DB"}, status=status.HTTP_400_BAD_REQUEST)
        
# 회원가입 버튼을 눌렀을때 사용하는 API
# TODO: Create가 안됨 확인 필요
class RegisterAPIView(APIView):
    def post(self, request):
        
        # data를 json형태로 주면 될듯.
        name = request.data.get("name")
        birth = request.data.get("birth")
        phone = request.data.get("phone")
        email = request.data.get("email")
        id = request.data.get("id")
        pw = request.data.get("password")
        if not name or not birth or not phone or not email or not id or not pw:
            return Response({"error": "Something none in user data"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            Users.objects.create(id=id, pw=pw, name=name, birth=birth, phone=phone, email=email, register_day=date.today(), first_login=0)
            return Response({"error": "Create new user"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Fail create new user"}, status=status.HTTP_400_BAD_REQUEST)

# 중복 아이디 체크
class CheckIDAPIView(APIView):
    def post(self, request):
        username = request.data.get('id')
        if not username:
            return Response({"username":None}, status.HTTP_400_BAD_REQUEST)
         # db check
        try:
            user = Users.objects.get(id=username)
        except Exception:
            # 못 찾으면 괜찮
            return Response(status=status.HTTP_200_OK)
        # 찾으면 이상
        return Response({"error": "Invalid username"}, status=status.HTTP_401_UNAUTHORIZED)
            
# 아이디 찾기
# phone, authNo, datetime
class FoundIDAPIView(APIView):
    def post(self, request):
        # front phone
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "phone required."}, status=status.HTTP_400_BAD_REQUEST)
        
        authcode = random.randint(1000, 9999)
        
        twilio = Twilio()
        twilio.send_message(authcode)
        
        try:
            data=AuthPhoneTable.objects.get(phone=phone)
        except: # phone이 없으면 생성
            AuthPhoneTable.objects.create(phone=phone, authNo=authcode, datetime=timezone.now())
        else:   # SNS에 구독 대기중이 사라진 경우 update 필요
            AuthPhoneTable.objects.filter(phone=phone).update(authNo=authcode) 
            AuthPhoneTable.objects.filter(phone=phone).update(datetime=timezone.now())
        return Response(status=status.HTTP_200_OK)

# 아이디 찾기 (확인용)
# 시간 확인 -> 인증번호 확인 -> status_200
class CheckAuthIDAPIView(APIView):
    def post(self, request):
        # front phone
        number = request.data.get("number")
        phone = request.data.get("phone")
        if not phone or not number:
            return Response({"error": "Phone No. or Auth No. is required."}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            data=AuthPhoneTable.objects.get(phone=phone)
        except:
            return Response({"error": "There is no phone in DB"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            second = (timezone.now() - data.datetime).total_seconds()
            givesecond = 60 * 10 # 10분
            if second < givesecond:
                if number == data.authNo:
                    user = Users.objects.get(phone=phone)
                    return Response({"id":f"{user.id}", "register_day":f"{user.register_day}"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error":"AuthCode is not same"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"Time has expired."}, status=status.HTTP_400_BAD_REQUEST)
# class CheckAuthIDAPIView():
    
# 비밀번호 찾기
class FoundPWAPIView(APIView):
    def post(self, request):
        # front phone
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "phone required."}, status=status.HTTP_400_BAD_REQUEST)
        
        authcode = random.randint(1000, 9999)
        
        twilio = Twilio()
        twilio.send_message(authcode)
        
        try:
            data=AuthPhoneTable.objects.get(phone=phone)
        except: # phone이 없으면 생성
            AuthPhoneTable.objects.create(phone=phone, authNo=authcode, datetime=timezone)
        else:   # SNS에 구독 대기중이 사라진 경우 update 필요
            AuthPhoneTable.objects.filter(phone=phone).update(authNo=authcode) 
            AuthPhoneTable.objects.filter(phone=phone).update(datetime=timezone.now())
        
        return Response(status=status.HTTP_200_OK)

# 비밀번호 찾기 (확인용)
class CheckAuthPWAPIView(APIView):
    def post(self, request):
        # front phone
        phone = request.data.get("phone")
        username = request.data.get("id")
        number = request.data.get("number")
        
        if not phone and not username or not number:
            return Response({"error": "Phone or Username or AuthCode is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # User data 가져오기 
        try:
            user = Users.objects.get(id=username)
        except Exception:
            pass
        else:
            pass
        ###### Phone data 가져오기 
        try:
            data=AuthPhoneTable.objects.get(phone=phone)
        except:
            pass
        else:
            pass
        ###### 인증 코드 Check
        second = (timezone.now() - data.datetime).total_seconds()
        givesecond = 60 * 10 # 10분
        if second < givesecond:
            if number == data.authNo:
                pass
            else:
                return Response({"error":"AuthCode is not same"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"Time has expired."}, status=status.HTTP_400_BAD_REQUEST)
        ####### ID, Phone No Check
        if not user or not data:
            return Response({"error":"ID or Phone No is wrong"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_200_OK)
                
class ChangePWAPIView(APIView):
    # update
    def post(self, request):
        id = request.data.get("id")
        pw = request.data.get("pw")
        if not id or not pw:
            return Response({"error": "ID or Password is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = Users.objects.get(id=id)
            Users.objects.filter(id=user.id).update(pw=pw)
            
            res = Response({
                "message": "비밀번호 수정 성공",
                },
                status=status.HTTP_200_OK
            )
            return res
        except jwt.exceptions.InvalidTokenError:
            return Response({"message": "로그인이 만료되었습니다. 로그인해 주세요."}, status=status.HTTP_404_NOT_FOUND)

# 홈화면 : Token Check
# 로그인 상태 API
class AuthAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        # TODO : DynamoDB에서 사용자가 저장한 시간표 response
        try:
            user = request.user
            print(user)
            print("\n\n")
            res = Response({
                "message": "로그인 중입니다.",
                },
                status=status.HTTP_200_OK
            )
            return res
        except jwt.exceptions.InvalidTokenError:
            return Response({"message": "로그인이 만료되었습니다. 로그인해 주세요."}, status=status.HTTP_404_NOT_FOUND)

# 최종 성향 저장
class TasteAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        #배열로 보내면 
        data = request.data.get("taste")
        id = request.data.get("id")
        
        am_pm = data[0]
        first_class = data[1]
        space_time = data[2]

        try:
            user = Users.objects.get(id=id)
            Users.objects.filter(id=user.id).update(am_pm=am_pm)
            Users.objects.filter(id=user.id).update(first_class=first_class)
            Users.objects.filter(id=user.id).update(space_time=space_time)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_200_OK)
        
class HomeTimetableAPIView(APIView):
    def post(self, request):
        id = request.data.get("id")
        
        user = Users.objects.get(id=id)
        print(type(user.user_id))
        
        dynamoDB = DynamoDBModel()
        
        data = dynamoDB.get_item({"user_id":user.user_id})
        
        for item in data['homepage_timetable']:
            item['time'] = item['time'] / 100
            item['duration'] = item['duration'] / 100
            
        print(data)
        
        return Response(
            {"course": data},
            status=status.HTTP_200_OK
            )