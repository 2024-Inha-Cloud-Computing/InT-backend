#!/bin/bash

# 프로젝트 디렉토리로 이동
cd /home/ubuntu/environment/

# 서버 시작
streamlit run chatbot_streamlit.py &

cd InT

python3 manage.py runserver 0.0.0.0:8000 &
