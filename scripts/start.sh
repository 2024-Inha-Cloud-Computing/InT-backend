#!/bin/bash

# 프로젝트 디렉터리로 이동
cd /home/ubuntu/environment/new_deploy

# 서버 시작
#streamlit run chatbot_streamlit.py &

pwd > pwd1.txt
ls > ls1.txt 

cd InT

pwd > pwd.txt
ls > ls.txt 

python manage.py runserver 0.0.0.0:8000 &
