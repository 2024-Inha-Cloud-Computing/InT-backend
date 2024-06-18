from django.urls import path, include
from .views import (AllCourseAPIView, FindCourseAPIView, 
            FirstFilteringTimetableAPIView, SndFilLikeProfAPIView, MakeTimeTableAPIView, 
            FirstFilteringDecideAPIView, DepartmentsAPIView, GetScheduleAPIView, ManualAddManualAPIView,
            AddCourseAPIView, RemoveCourseAPIView, ALLFindCourseAPIView, FilteringCourseAPIView)

urlpatterns = [
    path("allCourse/", AllCourseAPIView.as_view(), name="allcourse"),
    path("findCourse/", FindCourseAPIView.as_view(), name="findcourse"),
    path("firstFilteringTimetable/", FirstFilteringTimetableAPIView.as_view(), name="firstfilteringtimetable"),
    path("sndFilLikeProf/", SndFilLikeProfAPIView.as_view(), name="sndfillikeprof"),
    path("sndFilDecide/", MakeTimeTableAPIView.as_view(), name="sndfildecide"),
    path("firstFilteringDecide/", FirstFilteringDecideAPIView.as_view(), name="firstfilteringdecide"),
    path("departments/", DepartmentsAPIView.as_view(), name="department"),
    path("getSchedule/", GetScheduleAPIView().as_view(), name="getschedule"),
    path("manualAddManual/", ManualAddManualAPIView().as_view(), name="manualaddmanual"),
    path("addCourse/", AddCourseAPIView().as_view(), name="addcourse"),
    path("removeCourse/", RemoveCourseAPIView().as_view(), name="removecourse"),
    path("allFindCourse/", ALLFindCourseAPIView().as_view(), name="allfindcourse"),
    path("filteringCourse/", FilteringCourseAPIView().as_view(), name="filteringcourse")
]
