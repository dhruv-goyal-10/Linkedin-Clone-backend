"""LinkedIn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('account/register/', RegistrationAPIView.as_view()),
    # path('create/', AccountCreationAPIView.as_view()),
    path('account/login/', LoginAPIView.as_view()),
    path('account/oauth/', OAuthAPIView.as_view()),
    path('otp/email/send/', SendEmailOTP.as_view()),
    path('otp/email/verify/', VerifyEmailOTP.as_view()),
    path('otp/phone/send/', SendPhoneOTP.as_view()),
    path('otp/phone/verify/', VerifyPhoneOTP.as_view()),
    path('password/forget/', ForgetPassword.as_view()),
    
    # path('password/change/', ChangePassword.as_view()),
    # path('temp/', Temp.as_view()),
]
