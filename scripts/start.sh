#!/bin/bash

# 프로젝트 디렉터리로 이동
cd ~/environment

# 서버 시작
streamlit run chatbot_streamlit.py

cd InT

python manage.py runserver 0.0.0.0:8000

cd ..