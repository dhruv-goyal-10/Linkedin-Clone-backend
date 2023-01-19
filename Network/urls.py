from django.urls import path
from Profile.views import *
from Network.views import *

urlpatterns = [
    path('connection/request/send/', ConnectionRequestSendView.as_view()),
    path('connection/request/send/action/', ConnectionRequestSendActionView.as_view()),
    path('connection/request/received/', ConnectionRequestReceiveView.as_view()),
    path('connection/request/received/action/', ConnectionRequestReceiveActionView.as_view()),
    path('connection/remove/', ConnectionRemoveView.as_view()),
    
    ]
