from os import stat, write
from pickletools import read_uint1
from django.contrib.auth import get_user_model, authenticate
from django.db.models import fields
from django.core.exceptions import ValidationError
import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.forms.models import model_to_dict
from .models import User, EmailOTP
from .utils import CustomValidation, normalize_email
from django.core.validators import RegexValidator
from . import google
from decouple import config
import random
                

class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,
                                   validators= [RegexValidator(regex="^[A-Za-z0-9._%+-]+@gmail\.com$", 
                                   message='Try with a Different Email Domain',),],
                                   write_only=True)
    
    password = serializers.CharField(write_only=True, min_length=8)
    message = serializers.CharField(read_only=True)
    
    
    def validate_email(self, email):
        email = normalize_email(email)
        if User.objects.filter(email__exact = email).exists():
            raise CustomValidation(detail ="Someone's already using that email",
                                field = 'email',
                                status_code= status.HTTP_409_CONFLICT)
        return email
    
    def validate_password(self, password):
        
        if not re.findall('\d', password):
            raise ValidationError("The password must contain at least 1 digit.")
      
        if not re.findall('[A-Z]', password):
            raise ValidationError("The password must contain at least 1 uppercase letter.")
        
        if not re.findall('[a-z]', password):
            raise ValidationError("The password must contain at least 1 lowercase letter.")
        
        if not re.findall('[!@#$%&]', password):
            raise ValidationError("The password must contain at least 1 special character.")
        
        return password
    
    def create(self, validated_data): 
        return{
            'message': "User can proceed with the details"
            }
        
    

class AccountCreationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,
                                   validators= [RegexValidator(regex="^[A-Za-z0-9._%+-]+@gmail\.com$", 
                                   message='Try with a Different Email Domain',),],
                                   write_only=True)
    
    password = serializers.CharField(write_only=True, min_length=8)
    email_otp = serializers.IntegerField(write_only=True)
    phone_otp = serializers.IntegerField(write_only=True)
    message = serializers.CharField(read_only=True)
    
    def validate_email(self, email):
        email = normalize_email(email)
        if User.objects.filter(email__exact = email).exists():
            raise CustomValidation(detail ="Someone's already using that email",
                                    field = 'email',
                                    status_code= status.HTTP_409_CONFLICT)
        return email
    
    def validate_email_otp(self, email_otp):
        email = normalize_email(self.initial_data('email'))
        
        try:
            otp_object = EmailOTP.objects.get(email=email)
            if email_otp != otp_object.otp:
                raise CustomValidation(detail = "Invalid email OTP",
                                        field = 'email_otp',
                                        status_code= status.HTTP_401_UNAUTHORIZED)
            otp_object.delete()
        
        except EmailOTP.DoesNotExist:
            raise CustomValidation(detail = "Unable to confirm your Email OTP. \n Please login Again",
                                    field = 'email_otp',
                                    status_code= status.HTTP_502_BAD_GATEWAY)
        return email_otp
        
    def validate_phone_otp(self, phone_otp):
        return phone_otp
        
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        try:
            User.objects.create_user(email = email, password = password)
            return{
            'message': "User Created Successfully"
            }
        except:
            raise CustomValidation(detail ="Some error occured from our side. Please try again later.",
                                field = 'email',
                                status_code= status.HTTP_502_BAD_GATEWAY)
            
        

class LoginSerializer(serializers.Serializer):
    message= serializers.CharField(read_only=True)
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    tokens = serializers.JSONField(read_only=True)
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
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
        
    def create(self, validated_data):
        return validated_data
    
    
class OAuthSerializer(serializers.Serializer):
    
    registered= serializers.BooleanField(default=False, read_only=True)
    oauth_token = serializers.CharField(write_only=True, min_length=8)
    tokens = serializers.JSONField(read_only=True)
    email_otp= serializers.IntegerField(read_only=True)
    
    
    def validate(self, attrs):
        oauth_token = attrs.get('oauth_token')
        user_data = google.Google.validate(oauth_token)
        print(user_data)
        
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )
            
        if user_data['aud'] != config('GOOGLE_CLIENT_ID'):
            raise CustomValidation(detail="Incorrect authentication credentials.",
                                   field= "oauth_token",
                                   status_code=status.HTTP_401_UNAUTHORIZED)
            
        email= normalize_email(user_data['email'])
        try:
            user = User.objects.get(email=email)
            print(user.get_tokens)
            return{
                'registered': True,
                'tokens': user.get_tokens
            }
            
        except:
            random_otp = random.randint(100000, 999999)
            updated_values = {'otp': random_otp}
            EmailOTP.objects.update_or_create(email=email,
                                              defaults=updated_values)
            return{
                'registered': False,
                'email_otp': random_otp,
            }
    
    def create(self, validated_data):
        return validated_data
    

class SendEmailOTPSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    
    def create(self, validated_data):
        
        return super().create(validated_data)
    
        

class Temp(serializers.Serializer):
    
    email = serializers.EmailField()
    name = serializers.CharField()
        