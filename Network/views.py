from rest_framework import status
from rest_framework.generics import *
from Network.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import *
from Profile.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404



class ConnectionRequestSendView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionRequestSerializer
    
    def get_queryset(self):
        profile = get_object_or_404(Profile, user = self.request.user.id)
        return ConnectionRequest.objects.filter(sender = profile).exclude(state= "Withdrawn")
    
    def post(self, request, *args, **kwargs):
        
        sender_profile = get_object_or_404(Profile, user = self.request.user.id)
        request.data.update({"sender" : sender_profile.id})
        try:
            username = self.request.data['reciever']
        except KeyError :
            return super().post(request, *args, **kwargs)
        reciever_profile = get_object_or_404(Profile, username = username)
        request.data.update({"reciever" : reciever_profile.id})
        return super().post(request, *args, **kwargs)
    
    
class ConnectionRequestReceiveView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionRequestSerializer
    
    def get_queryset(self):
        profile = get_object_or_404(Profile, user = self.request.user.id)
        return ConnectionRequest.objects.filter(reciever = profile, state = "Pending")
    
    
class ConnectionRequestSendActionView(UpdateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionRequestSerializer
    
    def get_queryset(self):
        profile = get_object_or_404(Profile, user = self.request.user.id)
        return ConnectionRequest.objects.filter(reciever = profile, state = "Pending")
    
class ConnectionRequestReceiveActionView(UpdateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionRequestSerializer
    
    def get_queryset(self):
        profile = get_object_or_404(Profile, user = self.request.user.id)
        return ConnectionRequest.objects.filter(reciever = profile, state = "Pending")
    
class ConnectionRemoveView(GenericAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionRequestSerializer
    
    def post(self, request, *args, **kwargs):
        pass
    
    # def get_queryset(self):
    #     profile = get_object_or_404(Profile, user = self.request.user.id)
    #     return ConnectionRequest.objects.filter(reciever = profile, state = "Pending")
    
    