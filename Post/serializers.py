from rest_framework import serializers, status
from .models import *
from Post.models import *
from Profile.serializers import ShortProfileSerializer
from Authentication.utils import CustomValidation
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
import re
from Notification.models import *
 
class PostImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PostImages
        fields = ['image']   
        
 
 
class HashTagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HashTag
        fields = ['topic']   
       
       
       
       
       
class PostSerializer(serializers.ModelSerializer):
    
    images = serializers.ListField(
        child=serializers.ImageField(), write_only = True, required = False )
    
    post_owner_profile = ShortProfileSerializer(source = "post_owner", read_only = True)
    
    class Meta:
        model = Post
        exclude = ['saved_by', 'viewed_by']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        viewer_profile = get_object_or_404(Profile, user = self.context['request'].user)
        post_reaction = PostReaction.objects.filter(post = instance,
                                                   reacted_by = viewer_profile)
        
        data['self_reaction'] = False
        if post_reaction.exists():
            data['self_reaction'] = True
            data['self_reaction_data'] = PostReactionSerializer(instance=post_reaction[0],
                                                                context = {"request": self.context['request']}).data
        
        if post_reaction.exists():
            data['self_reaction_data'] = PostReactionSerializer(instance=post_reaction[0],
                                                                context = {"request": self.context['request']}).data
            
        # ---- To avoid loop of continous serialization --------
        count = 0
        try:
            count = self.context['count']
        except KeyError:
            pass
        # ------------------------------------------------------
        if instance.parent_post is not None and count == 0:
            data['parent_post_data'] = PostSerializer(instance = instance.parent_post,
                                                      context = {"request": self.context['request'], "count": 1}).data
        
        post_images = PostImages.objects.filter(post = instance)
        data['images_data'] = PostImageSerializer(instance = post_images , many = True).data
        
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['reactions_count'] = len(data.pop('reacted_by'))
        data['reacted_by'] = ShortProfileSerializer(instance = instance.reacted_by, many = True).data[:2]
        data['hashtags'] = HashTagSerializer(instance = instance.hashtags.all(), many = True).data
        data['reposts_count'] = Post.objects.filter(parent_post = instance).count()
        
        post_comments = Comment.objects.filter(post = instance)
        replies_count=0
        for post_comment in post_comments:
            replies_count += post_comment.commentreply_set.all().count()
        data['comments_count'] = len(data.pop('commented_by')) + replies_count
        
        return data
        
        
    def create(self, validated_data):
        
        try:
            images = validated_data.pop('images')
        except KeyError:
            images = []
        
        post = super().create(validated_data)
        
        topics = set(re.findall(r'\B#\w*[a-zA-Z]+\w*', validated_data['text']))
        for topic in topics:
            hashtag = HashTag.objects.get_or_create(topic = topic)[0]
            hashtag.associated_posts.add(post)
        
        post_images_list=[]
        for image in images: 
            post_images_list.append(
                PostImages(post = post, image = image)
            )
        if post_images_list:
            PostImages.objects.bulk_create(post_images_list)
        return post


   
   
class ReactionTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReactionType 
        fields = "__all__"
    
class PostReactionSerializer(serializers.ModelSerializer):
    
    reacted_by_profile = ShortProfileSerializer(source = "reacted_by",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    
    class Meta:
        model = PostReaction
        fields = "__all__"
        
    
    def create(self, validated_data):
        post_reaction = super().create(validated_data)
        Notification.objects.create(action = post_reaction.id,
                                    target = post_reaction.post.post_owner,
                                    source = post_reaction.reacted_by,
                                    type = NotificationType.objects.get(type = "post_reaction"))
        return post_reaction
        
        
class SinglePostReactionSerializer(serializers.ModelSerializer):
    
    reacted_by_profile = ShortProfileSerializer(source = "reacted_by",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    post_data = PostSerializer(source = "post", read_only = True)
    
    class Meta:
        model = PostReaction
        fields = "__all__"
        
        
class PostCommentSerializer(serializers.ModelSerializer):
    
    comment_owner_profile = ShortProfileSerializer(source = "comment_owner",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    
    class Meta:
        model = Comment
        fields = "__all__"


    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        viewer_profile = get_object_or_404(Profile, user = self.context['request'].user)
        comment_reaction = CommentReaction.objects.filter(comment = instance,
                                                   reaction_owner = viewer_profile)
        
        data['self_reaction'] = False
        if comment_reaction.exists():
            data['self_reaction'] = True
            data['self_reaction_data'] = CommentReactionSerializer(instance=comment_reaction[0],
                                                                   context = {"request": self.context['request']}).data
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['reactions_count'] = len(data.pop('reacted_by'))
        data['replies_count'] = len(data.pop('replied_by'))
        return data
    
    def create(self, validated_data):
        comment =  super().create(validated_data)
        Notification.objects.create(action = comment.id,
                                    target = comment.post.post_owner,
                                    source = comment.comment_owner,
                                    type = NotificationType.objects.get(type = "commented"))
        return comment
    
class SinglePostCommentSerializer(serializers.ModelSerializer):
    
    comment_owner_profile = ShortProfileSerializer(source = "comment_owner",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    post_data = PostSerializer(source = "post", read_only = True)
    
    class Meta:
        model = Comment
        fields = "__all__"


    def to_representation(self, instance):
        data = super().to_representation(instance)
        viewer_profile = get_object_or_404(Profile, user = self.context['request'].user)
        comment_reaction = CommentReaction.objects.filter(comment = instance,
                                                         reaction_owner = viewer_profile)
        
        data['self_reaction'] = False
        if comment_reaction.exists():
            data['self_reaction'] = True
            data['self_reaction_data'] = CommentReactionSerializer(instance=comment_reaction[0],
                                                                   context = {"request": self.context['request']}).data
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['reactions_count'] = len(data.pop('reacted_by'))
        data['replies_count'] = len(data.pop('replied_by'))
        return data
    
    
class CommentReactionSerializer(serializers.ModelSerializer):
    
    reaction_owner_profile = ShortProfileSerializer(source = "reaction_owner",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    
    class Meta:
        model = CommentReaction
        fields = "__all__"
        
    def create(self, validated_data):
        comment_reaction =  super().create(validated_data)
        Notification.objects.create(action = comment_reaction.id,
                                    target = comment_reaction.comment.post.post_owner,
                                    source = comment_reaction.reaction_owner,
                                    type = NotificationType.objects.get(type = "comment_reaction"))
        return comment_reaction
class SingleCommentReactionSerializer(serializers.ModelSerializer):
    
    reaction_owner_profile = ShortProfileSerializer(source = "reaction_owner",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    comment_data = SinglePostCommentSerializer(source = "comment", read_only = True)
    
    class Meta:
        model = CommentReaction
        fields = "__all__"
        
        
        
class ReplySerializer(serializers.ModelSerializer):
    
    reply_owner_profile = ShortProfileSerializer(source = "reply_owner",read_only = True)
    
    class Meta:
        model = CommentReply
        fields = "__all__"


    def to_representation(self, instance):
        data = super().to_representation(instance)
        viewer_profile = get_object_or_404(Profile, user = self.context['request'].user)
        reply_reaction = ReplyReaction.objects.filter(comment_reply = instance,
                                                   reaction_owner = viewer_profile)
        
        data['self_reaction'] = False
        if reply_reaction.exists():
            data['self_reaction'] = True
            data['self_reaction_data'] = ReplyReactionSerializer(instance=reply_reaction[0],
                                                                 context = {"request": self.context['request']}).data
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['reactions_count'] = len(data.pop('reacted_by'))
        return data

    def create(self, validated_data):
        reply = super().create(validated_data)
        Notification.objects.create(action = reply.id,
                                    target = reply.comment.post.post_owner,
                                    source = reply.reply_owner,
                                    type = NotificationType.objects.get(type = "reply"))
        return reply
    
class SingleReplySerializer(serializers.ModelSerializer):
    
    reply_owner_profile = ShortProfileSerializer(source = "reply_owner",read_only = True)
    class Meta:
        model = CommentReply
        fields = "__all__"


    def to_representation(self, instance):
        data = super().to_representation(instance)
        viewer_profile = get_object_or_404(Profile, user = self.context['request'].user)
        reply_reaction = ReplyReaction.objects.filter(comment_reply = instance,
                                                    reaction_owner = viewer_profile)
        
        data['self_reaction'] = False
        if reply_reaction.exists():
            data['self_reaction'] = True
            data['self_reaction_data'] = ReplyReactionSerializer(instance=reply_reaction[0],
                                                                 context = {"request": self.context['request']}).data
        
        data['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        data['comment_data'] = PostCommentSerializer(instance=instance.comment,
                                                     context = {"request": self.context['request']}).data
        data['post_data'] = PostSerializer(instance=instance.comment.post,
                                           context = {"request": self.context['request']}).data
        data['reactions_count'] = len(data.pop('reacted_by'))
        return data
    
class ReplyReactionSerializer(serializers.ModelSerializer):
    
    reaction_owner_profile = ShortProfileSerializer(source = "reaction_owner",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    
    class Meta:
        model = ReplyReaction
        fields = "__all__"
        
    def create(self, validated_data):
        reply_reaction = super().create(validated_data)
        Notification.objects.create(action = reply_reaction.id,
                                    target = reply_reaction.comment_reply.comment.post.post_owner,
                                    source = reply_reaction.reaction_owner,
                                    type = NotificationType.objects.get(type = "reply_reaction"))
        return reply_reaction
        
class SingleReplyReactionSerializer(serializers.ModelSerializer):
    
    reaction_owner_profile = ShortProfileSerializer(source = "reaction_owner",read_only = True)
    reaction = ReactionTypeSerializer(source = "reaction_type", read_only = True)
    
    class Meta:
        model = ReplyReaction
        fields = "__all__"
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['comment_data'] = PostCommentSerializer(instance=instance.comment_reply.comment,
                                                     context = {"request": self.context['request']}).data
        data['post_data'] = PostSerializer(instance=instance.comment_reply.comment.post,
                                           context = {"request": self.context['request']}).data
        data['reply_data'] = ReplySerializer(instance=instance.comment_reply,
                                             context = {"request": self.context['request']}).data
        return data
    
    

class PostBookmarkSerializer(serializers.ModelSerializer):
    
    post_id = serializers.IntegerField(write_only = True)
    
    class Meta:
        model = Post
        exclude = ['viewed_by', 'reacted_by', 'commented_by']
        extra_kwargs = {'post_id': {'required': True},
                        'text': {'required': False},}
        
        
    def create(self, validated_data):
        
        post = get_object_or_404(Post, id = validated_data['post_id'])
        profile = get_object_or_404(Profile,user = self.context['request'].user)
        
        if profile.saved_posts.filter(id = post.id).exists():
            post.saved_by.remove(profile)
        else:
            post.saved_by.add(profile)
        return post
    
        
    def to_representation(self, instance):
        data = PostSerializer(instance = instance,context = {"request": self.context['request']} ).data
        return data






# class HashTagFollowSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = HashTag
#         fields = ['topic']   
        
        
        
class ActivitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        exclude = ['saved_by', 'viewed_by']
        
    def to_representation(self, instance):
        
        if type(instance) is Post:
            data = PostSerializer(instance = instance, context = {"request": self.context['request']}).data
            data['message'] = f"{instance.post_owner.full_name} posted this."
            
        elif type(instance) is PostReaction:
            
            data = SinglePostReactionSerializer(instance = instance, context = {"request": self.context['request']}).data
            data['message'] = f"{instance.reacted_by.full_name} reacted to this post."
        
        elif type(instance) is Comment:
            data = SinglePostCommentSerializer(instance = instance,context = {"request": self.context['request']} ).data
            data['message'] = f"{instance.comment_owner.full_name} commented on this post."
            
        elif type(instance) is CommentReaction:
            data = SingleCommentReactionSerializer(instance = instance, context = {"request": self.context['request']}).data
            data['message'] = f"{instance.reaction_owner.full_name} reacted to the comment on this post."
        
        elif type(instance) is CommentReply:
            data = SingleReplySerializer(instance = instance,context = {"request": self.context['request']} ).data
            data['message'] = f"{instance.reply_owner.full_name} replied to comment on this post."
            
        elif type(instance) is ReplyReaction:
            data = SingleReplyReactionSerializer(instance = instance, context = {"request": self.context['request']}).data
            data['message'] = f"{instance.reaction_owner.full_name} reacted to a reply on this post."
            
        return data
        