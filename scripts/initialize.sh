#!/bin/bash

# 프로젝트 디렉토리로 이동
cd /home/ubuntu/environment/new_deploy

# 압축 파일 해제
unzip deploy.zip

# 압축 파일 삭제
rm deploy.zip

# Python 가상 환경 설정 및 활성화
python3 -m venv venv
source venv/bin/activate

# 운영체제 패키지 업데이트
sudo apt-get update

# 프로젝트 의존성 설치
pip install -r requirements.txt
