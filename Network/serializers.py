from rest_framework import serializers, status
from .models import *
from Authentication.utils import CustomValidation
import cloudinary
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from Profile.serializers import *

class ConnectionRequestSerializer(serializers.ModelSerializer):
    
    sender_data = ShortProfileSerializer(source = "sender", read_only = True)
    reciever_data = ShortProfileSerializer(source = "reciever", read_only = True)
    class Meta:
        model = ConnectionRequest
        fields = "__all__"
    
    
    def create(self, validated_data):
        return super().create(validated_data)
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['state'] = "Pending"
        return data
    
    
# class EmploymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employment
#         fields = "__all__"