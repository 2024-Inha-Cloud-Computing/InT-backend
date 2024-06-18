import json
import logging
import time
import boto3
from botocore.exceptions import ClientError
from rest_framework.response import Response
from rest_framework import status

from pathlib import Path
from dotenv import dotenv_values

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).resolve().parent.parent
# .env 파일 경로
env_path = BASE_DIR / '.env'
# .env 파일 로드
config = dotenv_values(env_path)
# 환경 변수 가져오기
TOPIC_ARN = config['TOPIC_ARN']
SUB_EMAIL_ARN = config['SUB_EMAIL_ARN']
SUB_MOBILE_ARN = config['SUB_MOBILE_ARN']

class SnsWrapper:
    def __init__(self, sns_resource):
        self.sns_resource = sns_resource

    # SES 가입.
    def subscribe(self, topic, protocol, endpoint):
        try:
            subscription = topic.subscribe(
                Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True
            )
        except ClientError:
            Response(status.status_501_subscribe_error)
        else:
            return subscription

    # SES 삭제
    def delete_subscription(self, subscription):
        try:
            subscription.delete()
        except ClientError:
            Response(status.status_501_subscribtion)

    # 구독한 가입자.
    def list_subscriptions(self, topic):
        try:
            subs_iter = topic.subscriptions.all()
        except ClientError:
            subs_iter = None
        return subs_iter

    # 핸드폰 메시지 전송 (현재 사용x)
    def publish_text_message(self, phone_number, message):
        try:
            response = self.sns_resource.meta.client.publish(
                PhoneNumber=phone_number, Message=message
            )
            message_id = response["MessageId"]
        except ClientError:
            Response(status.status_501_publish_message)
            raise
        else:
            return message_id

    # 이메일 전송
    def publish_message(self, topic, message):
        try:
            response = topic.publish(Message=message)
            message_id = response["MessageId"]
        except ClientError:
            Response(status.status_501_publish_message)
        else:
            return message_id

class SNS_API():
    def __init__(self):
        self.sns_wrapper = SnsWrapper(boto3.resource(
            "sns",
            region_name='ap-southeast-1',
            ))
        self.topic_arn = TOPIC_ARN
        self.subscription_email_arn = SUB_EMAIL_ARN
        self.subscription_phone_arn = SUB_MOBILE_ARN
   
    def subscribe_by_email(self, new_email):
        topic = self.sns_wrapper.sns_resource.Topic(self.topic_arn)
        
        new_subscription = self.sns_wrapper.subscribe(topic, 'email', new_email)
        
        return new_subscription.arn
    
    def check_subscribe_by_email(self, subscription_arn):
        topic = self.sns_wrapper.sns_resource.Topic(self.topic_arn)
        
        list_subscription = self.sns_wrapper.list_subscriptions(topic)
        
        for sub in list_subscription:
            if sub.arn == subscription_arn:
                return True
        return False
    
    
    
    
    ###########################여기는 사용안하고 있음##############################
    # 이메일로 인증번호 전송
    def send_email_auth(self, email, auth_code):
        topic = self.sns_wrapper.sns_resource.Topic(self.topic_arn)
        
        res = self.sns_wrapper.publish_message(topic, auth_code)
    
    def send_message_by_phone(self, new_phone, auth_code):
        message = f"InT 인증번호: {auth_code}"
        new_phone = f"+82{new_phone[1:]}"
        
        print(new_phone)
        sns_client = boto3.client('sns', region_name='us-east-1')
        try:
            response = sns_client.publish(
                PhoneNumber=new_phone,
                Message=message
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error sending message: {e}")
        # res = self.sns_wrapper.publish_text_message(new_phone, message)
    
    
    
    def use_subscribe_find_id_pw_by_phone(self, new_phone):
        topic = self.sns_wrapper.sns_resource.Topic(self.topic_arn)
        
        new_subscription = self.sns_wrapper.subscribe(topic, 'sms', new_phone)
        
        return new_subscription.arn
        
    
    def check_subscribe_by_phone_give_id_pw(self, subscription_arn):
        topic = self.sns_wrapper.sns_resource.Topic(self.topic_arn)
        
        list_subscription = self.sns_wrapper.list_subscriptions(topic)
        
        for sub in list_subscription:
            if sub.arn == subscription_arn:
                return True
        return False
    
    def delete_subscribe_by_phone(self, subscription_arn):
        try: 
            self.sns_wrapper.delete_subscription(subscription_arn)
            return True
        except:
            return False
    ###########################################################