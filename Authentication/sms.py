from twilio.rest import Client 
from django.conf import settings


account_sid = settings.ACCOUNT_SID
auth_token = settings.AUTH_TOKEN
messaging_service_sid = settings.MESSAGING_SERVICE_SID

client = Client(account_sid, auth_token) 
 
def send_otp_to_phonenumber(phone_number,otp):
    
    message = client.messages.create(    
                                messaging_service_sid = messaging_service_sid,  
                                body= f"One Time Password (OTP) to verify your mobile number on Profolio is {otp}",    
                                to= f"+91{phone_number}"
                            ) 
    print(message.sid)
    