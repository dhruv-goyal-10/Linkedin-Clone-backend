from rest_framework import generics, serializers, status, mixins
from rest_framework.generics import *
import time, random
from Authentication.serializers import *
from django.core.mail import EmailMessage
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.exceptions import BadRequest, ObjectDoesNotExist
from .models import User


class RegistrationAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(RegistrationAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    

class AccountCreationAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AccountCreationSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(AccountCreationAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class LoginAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(LoginAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class OAuthAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OAuthSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(OAuthAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
    
class SendEmailOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OAuthSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(OAuthAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class VerifyEmailOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OAuthSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(OAuthAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class SendPhoneOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OAuthSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(OAuthAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class VerifyPhoneOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OAuthSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(OAuthAPIView, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class Temp(GenericAPIView):
    
    serializer_class= Temp
    def post(self, request, *args, **kwargs):
        return Response('Hello')
    pass
