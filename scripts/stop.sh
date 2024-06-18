#!/bin/bash

# Streamlit 프로세스 강제 종료
ps aux | grep "streamlit run chatbot_streamlit.py" | grep -v grep | awk '{print $2}' | xargs -r kill -9

# Django 프로세스 강제 종료
ps aux | grep "manage.py runserver" | grep -v grep | awk '{print $2}' | xargs -r kill -9
