#!/bin/bash

# 프로젝트 디렉터리로 이동
cd ~/environment

# Streamlit 프로세스 강제 종료 (추가 방법)
# ps aux를 사용하여 streamlit 프로세스를 찾고, grep으로 필터링하여 종료
ps aux | grep "streamlit run chatbot_streamlit.py" | grep -v grep | awk '{print $2}' | xargs -r kill -9

# Django 프로세스 강제 종료 (추가 방법)
# ps aux를 사용하여 manage.py runserver 프로세스를 찾고, grep으로 필터링하여 종료
ps aux | grep "manage.py runserver" | grep -v grep | awk '{print $2}' | xargs -r kill -9