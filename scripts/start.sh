#!/bin/bash

# 프로젝트 디렉터리로 이동
#cd /home/ubuntu/environment/new_deploy

# 서버 시작
#streamlit run chatbot_streamlit.py

#cd InT
#python manage.py runserver 0.0.0.0:8000

#!/bin/bash

# 디버깅 로그 파일 설정
LOGFILE="/home/ubuntu/environment/new_deploy/start.log"

echo "Starting application at $(date)" >> $LOGFILE

# 프로젝트 디렉토리로 이동
cd /home/ubuntu/environment/new_deploy

# 디버깅 메시지
echo "Activated directory: $(pwd)" >> $LOGFILE

# 서버 시작
{
  echo "Starting Streamlit server at $(date)"
  nohup streamlit run chatbot_streamlit.py &>> /home/ubuntu/environment/new_deploy/streamlit.log &
  echo "Streamlit server started at $(date)"

  cd InT
  echo "Activated directory for Django: $(pwd)"

  echo "Starting Django server at $(date)"
  nohup python manage.py runserver 0.0.0.0:8000 &>> /home/ubuntu/environment/new_deploy/django.log &
  echo "Django server started at $(date)"
} >> $LOGFILE 2>&1

