from rest_framework import serializers, status
from .models import *
from Notification.models import *
from Profile.serializers import ShortProfileSerializer, ProfileViewersSerializer
from django.shortcuts import get_object_or_404
from Post.serializers import *
from Profile.models import ProfileView
class NotificationSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Notification
        fields = "__all__"
    
    
    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        instance.seen = True
        instance.save()
        
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['source_profile'] = ShortProfileSerializer(instance = instance.source, context = {"request": self.context['request']}).data
        data['type'] = instance.type.type
        if instance.type.type == "post_reaction":
            try:
                data['post_reaction_data'] = SinglePostReactionSerializer(instance = get_object_or_404(PostReaction, id = instance.action),
                                                                         context = {"request": self.context['request']}).data
            except:
                data['post_reaction_data'] = "deleted"
                
        elif instance.type.type == "commented":
            try:
                data['comment_data'] = SinglePostCommentSerializer(instance = get_object_or_404(Comment, id = instance.action),
                                                                    context = {"request": self.context['request']}).data
            except:
                data['comment_data'] = "deleted"
                
        elif instance.type.type == "comment_reaction":
            try:
                data['comment_reaction_data'] = SingleCommentReactionSerializer(instance = get_object_or_404(CommentReaction, id = instance.action),
                                                                    context = {"request": self.context['request']}).data
            except:
                data['comment_reaction_data'] = "deleted"
                
        elif instance.type.type == "reply":
            try:
                data['reply_data'] = SingleReplySerializer(instance = get_object_or_404(CommentReply, id = instance.action),
                                                            context = {"request": self.context['request']}).data
            except:
                data['reply_data'] = "deleted"
                
        elif instance.type.type == "reply_reaction":
            try:
                data['reply_reaction_data'] = SingleReplyReactionSerializer(instance = get_object_or_404(ReplyReaction, id = instance.action),
                                                                            context = {"request": self.context['request']}).data
            except:
                data['reply_reaction_data'] = "deleted"
                
        elif instance.type.type == "profile_view":
            try:
                data['profile_view_data'] = ProfileViewersSerializer(instance = get_object_or_404(ProfileView, id = instance.action),
                                                                     context = {"request": self.context['request']}).data
            except:
                data['profile_view_data'] = "deleted"
                
        return data

        
        