from twilio.rest import Client

class Twilio:
    def __init__(self):
        self.account_sid = 'ACb896c81f5a4b46c1f82b8b28599754f1'
        self.auth_token = 'a77d578bde0a355082c577b03b9e83db'
        self.client = Client(self.account_sid, self.auth_token)
    
    def send_message(self, auth_code):
        message = self.client.messages.create(
          from_='+15708575298',
          body=f'InT 인증코드 : {auth_code}',
          to='+821053860853'
        )
    
        print(message.sid)