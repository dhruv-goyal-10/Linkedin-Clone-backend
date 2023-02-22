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
    serializer_class= RegistrationSerializer
    

# class AccountCreationAPIView(CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = AccountCreationSerializer
    
    
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class OAuthAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OAuthSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = OAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SendEmailOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendEmailOTPSerializer
    
    
class VerifyEmailOTP(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailOTPSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SendPhoneOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendPhoneOTPSerializer
    
    def create(self, request, *args, **kwargs):
        response = super(SendPhoneOTP, self).create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
    
class VerifyPhoneOTP(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = VerifyPhoneOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ForgetPassword(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgetPasswordSerializer
    
    def get_object(self):
        try:
            email = self.request.data['email']
            return User.objects.get(email=email)
        except KeyError:
            return None
    
    def update(self, request, *args, **kwargs):
        response = super(ForgetPassword, self).update(request, *args, **kwargs)
        response.data = {"message": "Password has been reset successfully" }
        return response
    
    
    

# class ChangePassword(UpdateAPIView):

#     serializer_class=ChangePasswordSerializer
    
#     def get_object(self):
#         return User.objects.get(email=self.request.data['email'])
    
#     def update(self, request, *args, **kwargs):
#         response = super(ForgetPassword, self).update(request, *args, **kwargs)
#         response.data = {"message": "Password has been updated successfully" }
#         return response
    
# class Temp(GenericAPIView):
    
#     serializer_class= Temp
#     def post(self, request, *args, **kwargs):
#         return Response('Hello')
#     pass

