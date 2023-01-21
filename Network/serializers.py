from rest_framework import serializers, status
from .models import *
from Authentication.utils import CustomValidation
import cloudinary
from django.shortcuts import get_object_or_404
from Profile.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class ConnectionRequestSerializer(serializers.ModelSerializer):
    
    sender_data = ShortProfileSerializer(source = "sender", read_only = True)
    reciever_data = ShortProfileSerializer(source = "reciever", read_only = True)
    class Meta:
        model = ConnectionRequest
        fields = "__all__"
        
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        sender_profile = data['sender'] 
        receiver_profile = data['reciever']
        
        try:
            obj = ConnectionRequest.objects.get(sender = sender_profile)
            if obj.state == "Withdrawn":
                if (datetime.now() - obj.created_at).days < 21:  
                    raise CustomValidation(detail="Your invitation to connect was not sent. You can resend your invitation to connect 3 weeks from when you withdrew.",
                                            field= "detail",
                                            status_code=status.HTTP_401_UNAUTHORIZED)
                else:
                    obj.delete()
            else:
                raise CustomValidation(detail="The person's request is already pending",
                                        field= "detail",
                                        status_code=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            pass

        if FirstConnections.objects.filter(owner = sender_profile, person = receiver_profile.user ).exists():
            raise CustomValidation(detail="You can't send a request to an already connected person.",
                                    field= "detail",
                                    status_code=status.HTTP_403_FORBIDDEN)
        return data  
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['state'] = "Pending"          # so that sender can't see if the request is ignored 
        return data
    
    
class ConnectionRequestAcceptSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(required = True, write_only = True)
    detail = serializers.CharField(read_only = True)
    
    def create(self, validated_data):
        
        reciever_profile = get_object_or_404(Profile, user = self.context.user)
        connection_request = get_object_or_404(ConnectionRequest, id = validated_data['id'],
                                               reciever = reciever_profile,
                                               state = "Pending")

        sender_profile = connection_request.sender
        # connection_degree_modification(sender_profile, reciever_profile)
        sender_profile.first_degrees.add(reciever_profile.user)
        reciever_profile.first_degrees.add(sender_profile.user)
        
        sender_profile.followers.add(reciever_profile.user)
        reciever_profile.followers.add(sender_profile.user)
        
        connection_request.delete()
        
        try:
            second_connection_request = ConnectionRequest.objects.get(sender = reciever_profile,
                                                                      reciever = sender_profile)
            second_connection_request.delete()
        except ObjectDoesNotExist:
            pass
        
        return {
            "detail": "The connection has been accepted successfully"
        }
        
        
# def connection_degree_modification(sender_profile, receiver_profile):
#     # for first_degrees in receiver_profile.first_degree:
#     #     print(first_degrees)
    
#     sender_profile.first_degrees.add(receiver_profile.user)
#     receiver_profile.first_degrees.add(sender_profile.user)
    
#     # print(sender_profile.first_degree.all())
#     print(sender_profile.first_degrees.all())
    
    
#     for profile in Profile.objects.all():
        
#         if profile.first_degrees.filter(id = sender_profile.user.id).exists():
#             obj = SecondConnections.objects.get_or_create(owner = profile, person = receiver_profile.user)[0]
#             obj.count = obj.count+1
#             obj.save()
            
#             for first_degree in receiver_profile.first_degrees.all():
#                 obj = ThirdConnections.objects.get_or_create(owner = profile, person = first_degree)[0]
#                 obj.count = obj.count+1
#                 obj.save()
            
#         if profile.first_degrees.filter(id = receiver_profile.user.id).exists():
#             obj = SecondConnections.objects.get_or_create(owner = profile, person = sender_profile.user)[0]
#             obj.count = obj.count+1
#             obj.save()
            
#             for first_degree in sender_profile.first_degrees.all():
#                 obj = ThirdConnections.objects.get_or_create(owner = profile, person = first_degree)[0]
#                 obj.count = obj.count+1
#                 obj.save()


#     #-------------- Second Degrees Modification ---------------------------
#     for first_degree in receiver_profile.first_degrees.all():
#         obj = SecondConnections.objects.get_or_create(owner = sender_profile, person = first_degree)[0]
#         obj.count = obj.count+1
#         obj.save()
        
#     for first_degree in sender_profile.first_degrees.all():
#         obj = SecondConnections.objects.get_or_create(owner = receiver_profile, person = first_degree)[0]
#         obj.count = obj.count+1
#         obj.save()
        
#     #-------------- Third Degrees Modification ---------------------------
    
#     for second_degree in receiver_profile.second_degrees.all():
#         obj = ThirdConnections.objects.get_or_create(owner = sender_profile, person = second_degree)[0]
#         obj.count = obj.count+1
#         obj.save()
        
#     for second_degree in sender_profile.second_degrees.all():
#         obj = ThirdConnections.objects.get_or_create(owner = receiver_profile, person = second_degree)[0]
#         obj.count = obj.count+1
#         obj.save()
        

#     sender_profile.first_degrees.add(receiver_profile.user)
#     receiver_profile.first_degrees.add(sender_profile.user)
    
    
    
    # sender_profile.first_degrees.add(receiver_profile.user)
    # receiver_profile.first_degrees.add(sender_profile.user)
        
        
    
    
    
class ConnectionRequestIgnoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionRequest
        fields = ["id"]
    
    def update(self, instance, validated_data):
        instance.state = "Ignored"
        instance.save()
        return instance
    
class ConnectionRequestWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionRequest
        fields = ["id"]
    
    def update(self, instance, validated_data):
        instance.state = "Withdrawn"
        instance.save()
        return instance
    
    
class ConnectionListSerializer(serializers.ModelSerializer):
    
    connection_data = ShortProfileSerializer(source = "owner", read_only = True)
    
    class Meta:
        model = FirstConnections
        fields = "__all__"
    
    
class FollowingSerializer(serializers.ModelSerializer):
    
    following_profile_data = ShortProfileSerializer(source = "profile", read_only = True)
    
    
    class Meta:
        model = Follow
        fields = "__all__"
        
class FollowersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Follow
        fields = "__all__"
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        follower_profile = get_object_or_404(Profile,user = data['follower'] )
        data['follower_profile_data'] = ShortProfileSerializer(instance = follower_profile, many = False).data
        return data
    

class MutualConnectionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"
        
    def to_representation(self, instance):
       
        profile = get_object_or_404(Profile, user = instance.id)
        data=ShortProfileSerializer(instance=profile, many = False).data
        
        return data
        
        
    
    
    
    
    