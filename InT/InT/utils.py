#ryu
# InT/utils.py

#import os
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key

def update_env_with_public_ip(env_path):
    try:
        # EC2 메타데이터 엔드포인트에서 퍼블릭 IP 주소 가져오기
        response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
        response.raise_for_status()
        public_ip = response.text

        # .env 파일이 존재하는지 확인하고 로드
        env_path = Path(env_path)
        if env_path.exists():
            load_dotenv(env_path)
        
        # .env 파일에 PUBLIC_IP 업데이트
        set_key(env_path, 'PUBLIC_IP', public_ip)
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
