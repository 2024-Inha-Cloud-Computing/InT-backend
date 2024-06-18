#!/bin/bash

# 프로젝트 디렉토리로 이동
cd /home/ubuntu/environment/new_deploy

# 운영체제 패키지 업데이트
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# 프로젝트 의존성 설치
python install_requirements.py

# 크롬 드라이버 설치
cd crawling_processing/crawling
#wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
