from django.urls import path
from .views import (RegisterAPIView, LoginAPIView, AuthAPIView, AuthCheckAPIView, AuthCheckInDBAPIView, CheckIDAPIView, RegisterAPIView, FoundIDAPIView, CheckAuthIDAPIView,
FoundPWAPIView, CheckAuthPWAPIView, ChangePWAPIView, TasteAPIView, HomeTimetableAPIView)

urlpatterns = [
    # 이메일 전송
    path("checkEmail/", AuthCheckAPIView.as_view(), name="checkemail"),
    # 이메일 verification Check
    path("checkEmailNumber/", AuthCheckInDBAPIView.as_view(), name="checkemailnumber"),
    # 로그인
    path("login/", LoginAPIView.as_view(), name="login"),
    # 아이디 중복 체크
    path("checkId/", CheckIDAPIView.as_view(), name="checkid"),
    # 홈 화면 : 사용자가 저장한 시간표가 보여야 함.
    path("", AuthAPIView.as_view(), name="timetable"),
    # 회원가입
    path("signup", RegisterAPIView.as_view(), name="signup"),
    # 핸드폰 전송
    path("checkPhone/", FoundIDAPIView.as_view(), name="checkid"),
    # 핸드폰 번호 체크
    path("checkPhoneNumber/", CheckAuthIDAPIView.as_view(), name="checkid"),

    path("findIdwithPhone/", FoundPWAPIView.as_view(), name="checkid"),
    path("checkPhoneNumber/", CheckAuthPWAPIView.as_view(), name="checkid"),
    path("changePw/", ChangePWAPIView.as_view(), name="checkid"),
    
    # 회원 성향 저장
    path("taste/", TasteAPIView().as_view(), name="taste"),
    # 시간표 홈
    path("homeTimetable/", HomeTimetableAPIView().as_view(), name="hometimetable"),
    
]
