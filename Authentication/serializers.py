from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from .emails import EMAIL
from .sms import send_otp_to_phonenumber
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailOTP, PhoneOTP
from .utils import CustomValidation, normalize_email,check_strong_password
from django.core.validators import RegexValidator
from . import google
from django.conf import settings
import random
from django.core.validators import MinValueValidator, MaxValueValidator

class RegistrationSerializer(serializers.Serializer):
    
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    email_otp = serializers.IntegerField(write_only=True)
    message = serializers.CharField(read_only=True)
    tokens = serializers.JSONField(read_only=True)
    
    
    def validate(self, attrs):
        email = normalize_email(attrs.get('email'))
        password = attrs.get('password')
        email_otp = attrs.get('email_otp')
        
        if User.objects.filter(email__exact = email).exists():
            raise CustomValidation(detail ="Someone's already using that email",
                                    field = 'email',
                                    status_code= status.HTTP_409_CONFLICT)
            
        if not check_strong_password(password):
            raise CustomValidation(detail ="The password does not match the required conditions",
                                    field = 'password',
                                    status_code= status.HTTP_406_NOT_ACCEPTABLE)
        
        if EmailOTP.objects.filter(email=email).exists():
            otp_object = EmailOTP.objects.get(email=email)

            if otp_object.otp_created_at + timedelta(minutes=5) < timezone.now() or otp_object.otp != email_otp:
                raise CustomValidation(detail="Email verification failed! Retry again",
                                field= "email_otp",
                                status_code=status.HTTP_401_UNAUTHORIZED)
            else:
                otp_object.delete()
                return super().validate(attrs)
        else:
            raise CustomValidation(detail="Email verification failed! Retry again",
                                field= "email_otp",
                                status_code=status.HTTP_401_UNAUTHORIZED)
            
    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], 
                                        password=validated_data['password'])
    
        return {
            "message": "User Created Successfully",
            "tokens" : user.get_tokens
        }


# class AccountCreationSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=255,
#                                    validators= [RegexValidator(regex="^[A-Za-z0-9._%+-]+@gmail\.com$", 
#                                    message='Try with a Different Email Domain',),],
#                                    write_only=True)
    
#     password = serializers.CharField(write_only=True, min_length=8)
#     email_otp = serializers.IntegerField(write_only=True)
#     message = serializers.CharField(read_only=True)
    
#     def validate_email(self, email):
#         email = normalize_email(email)
#         if User.objects.filter(email__exact = email).exists():
#             raise CustomValidation(detail ="Someone's already using that email",
#                                     field = 'email',
#                                     status_code= status.HTTP_409_CONFLICT)
#         return email
    
#     def validate_email_otp(self, email_otp):
#         email = normalize_email(self.initial_data('email'))
        
#         try:
#             otp_object = EmailOTP.objects.get(email=email)
#             if email_otp != otp_object.otp:
#                 raise CustomValidation(detail = "Invalid email OTP",
#                                         field = 'email_otp',
#                                         status_code= status.HTTP_401_UNAUTHORIZED)
#             otp_object.delete()
        
#         except EmailOTP.DoesNotExist:
#             raise CustomValidation(detail = "Unable to confirm your Email OTP. \n Please login Again",
#                                     field = 'email_otp',
#                                     status_code= status.HTTP_502_BAD_GATEWAY)
#         return email_otp
        
#     def validate_phone_otp(self, phone_otp):
#         return phone_otp
        
#     def create(self, validated_data):
#         email = validated_data.pop('email')
#         password = validated_data.pop('password')
#         try:
#             User.objects.create_user(email = email, password = password)
#             return{
#             'message': "User Created Successfully"
#             }
#         except:
#             raise CustomValidation(detail ="Some error occured from our side. Please try again later.",
#                                 field = 'email',
#                                 status_code= status.HTTP_502_BAD_GATEWAY)
            
        
class LoginSerializer(serializers.Serializer):
    
    message= serializers.CharField(read_only=True)
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    tokens = serializers.JSONField(read_only=True)
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        email = normalize_email(email)
        try:
            user = User.objects.get(email__iexact = email)
        except:
            raise CustomValidation(detail ='User is not registered with this Email Address',
                                   field = 'email',
                                   status_code= status.HTTP_404_NOT_FOUND)
        user = authenticate(
            email=email,
            password=password
        )

        if not user:
            raise CustomValidation(detail='Unable to authenticate with provided credentials',
                                   field= 'multiple',
                                   status_code= status.HTTP_401_UNAUTHORIZED)

        return {
            'message': "Login Successful",
            'tokens': user.get_tokens,
        }
        
class OAuthSerializer(serializers.Serializer):
    
    # registered= serializers.BooleanField(default=False, read_only=True)
    oauth_token = serializers.CharField(write_only=True)
    message = serializers.CharField(read_only=True)
    tokens = serializers.JSONField(read_only=True)
    
    def validate(self, attrs):
        oauth_token = attrs.get('oauth_token')
        user_data = google.Google.validate(oauth_token)
        print(user_data)
        
        try:
            user_data['sub']
        except:
            raise CustomValidation(detail='The token is invalid or expired. Please login again.',
                                   field= "oauth_token",
                                   status_code=status.HTTP_401_UNAUTHORIZED)
            
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise CustomValidation(detail="Incorrect authentication credentials.",
                                   field= "oauth_token",
                                   status_code=status.HTTP_401_UNAUTHORIZED)
            
        email= normalize_email(user_data['email'])
        
        try:
            user = User.objects.get(email=email)
            
            return{
                'message': "Login Successful",
                'tokens': user.get_tokens
            }
            
        except:
            
            user = User.objects.create_user(email=email,password=User.objects.make_random_password())
            return{
                'message': "User created successfully",
                'tokens': user.get_tokens
            }

class SendEmailOTPSerializer(serializers.Serializer):
    
    email = serializers.EmailField(write_only=True)
    context = serializers.CharField(write_only=True)
    message = serializers.CharField(read_only=True)
    
    def create(self, validated_data):
        email = validated_data['email']
        context = validated_data['context']
        email = normalize_email(email)
        if context != "register" and context!= "forget":
            raise CustomValidation(detail="Enter a valid Context",
                                    field= "context",
                                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
            
        if context == 'forget':
            if not User.objects.filter(email__iexact = email).exists():
                raise CustomValidation(detail="No user exists with this email",
                                        field= "email",
                                        status_code=status.HTTP_401_UNAUTHORIZED)
                
        if context == 'register':
            if User.objects.filter(email__iexact = email).exists():
                raise CustomValidation(detail="User already exists with this email",
                                        field= "email",
                                        status_code=status.HTTP_409_CONFLICT)
        
        
        if EmailOTP.objects.filter(email__iexact=email).exists():
            otp_object = EmailOTP.objects.get(email__iexact=email)
            
            if otp_object.otp_created_at + timedelta(minutes=1) >= timezone.now():
                raise CustomValidation(detail="WAIT FOR 1 minute before resending OTP",
                                        field= "otp",
                                        status_code=status.HTTP_408_REQUEST_TIMEOUT)
        
        try:
            
            otp = random.randint(100000, 999999)
            EMAIL.send_otp_via_email(email, otp)
            
            # Saving/ Updating the sent OTP in EmailOTP Model
            updated_values = {'otp': otp}
            EmailOTP.objects.update_or_create(email=email,
                                              defaults=updated_values)
            
            return{
                'message': "OTP has been sent to your mail"
            }
        except:
            raise CustomValidation(detail="Some error occured from our side",
                                field= "multiple",
                                status_code=status.HTTP_502_BAD_GATEWAY)
            
            
class VerifyEmailOTPSerializer(serializers.Serializer):
    
    email= serializers.EmailField(write_only=True)
    otp = serializers.IntegerField(write_only=True)
    message = serializers.CharField(read_only=True)
        
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        email = normalize_email(email)
        if EmailOTP.objects.filter(email=email).exists():
            otp_object = EmailOTP.objects.get(email=email)
            if otp_object.otp_created_at + timedelta(minutes=5) >= timezone.now():
                if otp_object.otp != otp :
                    raise CustomValidation(detail="Entered OTP is wrong",
                                    field= "otp",
                                    status_code=status.HTTP_401_UNAUTHORIZED)
                else:
                    # otp_object.delete()
                    return{
                        "message": "OTP has been verified Successfully"
                    }
            else:
                raise CustomValidation(detail="Your OTP has been expired! Generate a new OTP.",
                                    field= "otp",
                                    status_code=status.HTTP_408_REQUEST_TIMEOUT)
                
        else:
            raise CustomValidation(detail="Please generate an OTP first",
                                field= "email",
                                status_code=status.HTTP_401_UNAUTHORIZED)
            
            
class SendPhoneOTPSerializer(serializers.Serializer):
    
    phone_number = serializers.IntegerField(write_only=True,
                                            validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    message = serializers.CharField(read_only=True)
    
    def create(self, validated_data):
        phone_number = validated_data['phone_number']

        if PhoneOTP.objects.filter(phone_number=phone_number).exists():
            otp_object = PhoneOTP.objects.get(phone_number=phone_number)
            
            if otp_object.otp_created_at + timedelta(minutes=1) >= timezone.now():
                raise CustomValidation(detail="WAIT FOR 1 minute before resending OTP",
                                field= "multiple",
                                status_code=status.HTTP_408_REQUEST_TIMEOUT)
                
        try:
            otp = random.randint(100000, 999999)
            send_otp_to_phonenumber(phone_number, otp)
            
            # Saving/Updating the sent OTP in PhoneOTP Model
            updated_values = {'otp': otp}
            PhoneOTP.objects.update_or_create(phone_number=phone_number,
                                              defaults=updated_values)
            
            return{
                'message': "OTP has been successfully sent to your mobile number"
            }
        except:
            raise CustomValidation(detail="Some error occured from our side! Please try again later.",
                                field= "multiple",
                                status_code=status.HTTP_502_BAD_GATEWAY)

class VerifyPhoneOTPSerializer(serializers.Serializer):
    
    phone_number= serializers.IntegerField(write_only=True,
                                           validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    otp = serializers.IntegerField(write_only=True)
    message = serializers.CharField(read_only=True)
        
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp = attrs.get('otp')
        
        if PhoneOTP.objects.filter(phone_number=phone_number).exists():
            otp_object = PhoneOTP.objects.get(phone_number=phone_number)
            if otp_object.otp_created_at + timedelta(minutes=5) >= timezone.now():
                if otp_object.otp != otp :
                    raise CustomValidation(detail="Entered OTP is wrong",
                                    field= "otp",
                                    status_code=status.HTTP_401_UNAUTHORIZED)
                else:
                    otp_object.delete()
                    return{
                        "message": "OTP has been verified Successfully"
                    }
            else:
                raise CustomValidation(detail="Your OTP has been expired! Generate a new OTP.",
                                    field= "otp",
                                    status_code=status.HTTP_408_REQUEST_TIMEOUT)
                
        else:
            raise CustomValidation(detail="Please generate an OTP first",
                                    field= "otp",
                                    status_code=status.HTTP_400_BAD_REQUEST)

        
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    otp = serializers.IntegerField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        email = normalize_email(email)
        if EmailOTP.objects.filter(email=email).exists():
            otp_object=EmailOTP.objects.get(email=email)
            if otp_object.otp != otp or otp_object.otp_created_at + timedelta(minutes=5) < timezone.now():
                raise CustomValidation(detail="Entered OTP is wrong or expired",
                                field= "otp",
                                status_code=status.HTTP_401_UNAUTHORIZED)
                
        else:
            raise CustomValidation(detail="Unable to verify your OTP. Generate a new OTP",
                                field= "otp",
                                status_code=status.HTTP_401_UNAUTHORIZED)
            
            
        new_password = attrs.get('new_password')
        
        user = authenticate(email=email,password=new_password)
        if user is not None:
            raise CustomValidation(detail="Password entered is same as old one",
                                field= "password",
                                status_code=status.HTTP_406_NOT_ACCEPTABLE)
            
        if not check_strong_password(new_password):
            raise CustomValidation(detail="The password doesn't match the requirement conditions",
                                field= "password",
                                status_code=status.HTTP_406_NOT_ACCEPTABLE)
        
        otp_object.delete()
        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


# class ChangePasswordSerializer(serializers.Serializer):
#     pass


# class Temp(serializers.Serializer):
    
#     email = serializers.EmailField()
#     name = serializers.CharField()

        