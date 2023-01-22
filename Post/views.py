from rest_framework import status
from rest_framework.generics import *
from Post.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from itertools import chain
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramSimilarity
from rest_framework.views import APIView






class PostView(CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    
    
    def post(self, request, *args, **kwargs):
        
        print(request.data)
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        request.data.update({"post_owner" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)
        
    
class SinglePostView(RetrieveDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    
    queryset = Post.objects.all()
    
    
    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post,id = kwargs['pk'])
        if not post.post_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().delete(request, *args, **kwargs)


class PostReactionView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PostReactionSerializer
    
    
    def get_queryset(self):
        
        post = self.request.GET.get('post')
        return PostReaction.objects.filter(post = post)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"reacted_by" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)

    
class SinglePostReactionView(RetrieveUpdateDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SinglePostReactionSerializer
    
    queryset = PostReaction.objects.all()
    
    def patch(self, request, *args, **kwargs):
        
        post_reaction = get_object_or_404(PostReaction,id = kwargs['pk'])
        if not post_reaction.reacted_by.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
            
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        post_reaction = get_object_or_404(PostReaction,id = kwargs['pk'])
        if not post_reaction.reacted_by.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().delete(request, *args, **kwargs)
    
    
class PostCommentView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PostCommentSerializer
    
    def get_queryset(self):
        
        post = self.request.GET.get('post')
        return Comment.objects.filter(post = post)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"comment_owner" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)
    
    
    
class SinglePostCommentView(RetrieveDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SinglePostCommentSerializer
    
    queryset = Comment.objects.all()
    
    
    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment,id = kwargs['pk'])
        if not comment.comment_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().delete(request, *args, **kwargs)
    
    
class CommentReactionView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = CommentReactionSerializer
    
    
    def get_queryset(self):
        comment = self.request.GET.get('comment')
        comment = get_object_or_404(Comment, id = comment)
        return CommentReaction.objects.filter(comment = comment)

    def post(self, request, *args, **kwargs):
        request.data.update({"reaction_owner" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)
    
    
class SingleCommentReactionView(RetrieveUpdateDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SingleCommentReactionSerializer
    
    queryset = CommentReaction.objects.all()
    
    def patch(self, request, *args, **kwargs):
        
        comment_reaction = get_object_or_404(CommentReaction,id = kwargs['pk'])
        if not comment_reaction.reaction_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
        
        request.data.update({"comment" : comment_reaction.comment.id})
        return super().patch(request, *args, **kwargs)

    
    def delete(self, request, *args, **kwargs):
        
        comment_reaction = get_object_or_404(CommentReaction,id = kwargs['pk'])
        if not comment_reaction.reaction_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
            
        return super().delete(request, *args, **kwargs)
    
    
    
class ReplyView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ReplySerializer
    
    def get_queryset(self):
        comment = self.request.GET.get('comment')
        return CommentReply.objects.filter(comment = comment)
    
    def post(self, request, *args, **kwargs):
        request.data.update({"reply_owner" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)



class SingleReplyView(RetrieveDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SingleReplySerializer
    
    def get_queryset(self):
        return CommentReply.objects.all()
    
    def delete(self, request, *args, **kwargs):
        
        comment_reply = get_object_or_404(CommentReply,id = kwargs['pk'])
        if not comment_reply.reply_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReplyReactionView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ReplyReactionSerializer
    
    
    def get_queryset(self):
        reply = self.request.GET.get('reply')
        reply = get_object_or_404(CommentReply, id = reply)
        return ReplyReaction.objects.filter(comment_reply = reply)


    def post(self, request, *args, **kwargs):
        request.data.update({"reaction_owner" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)
    
    
class SingleReplyReactionView(RetrieveUpdateDestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SingleReplyReactionSerializer
    
    queryset = ReplyReaction.objects.all()
    
    def patch(self, request, *args, **kwargs):
        
        reply_reaction = get_object_or_404(ReplyReaction,id = kwargs['pk'])
        if not reply_reaction.reaction_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
        
        request.data.update({"reaction_owner" : reply_reaction.reaction_owner.id})
        return super().patch(request, *args, **kwargs)

    
    def delete(self, request, *args, **kwargs):
        
        reply_reaction = get_object_or_404(ReplyReaction,id = kwargs['pk'])
        if not reply_reaction.reaction_owner.user == self.request.user:
            return Response({"detail": "You are not allowed to perform this action"},
                            status = status.HTTP_405_METHOD_NOT_ALLOWED)
            
        return super().delete(request, *args, **kwargs)
    
    
class PostBookmarkView(ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PostBookmarkSerializer
    
    
    def get_queryset(self):
        viewer_profile = get_object_or_404(Profile, user = self.request.user)
        return viewer_profile.saved_posts.all()
    
    def post(self, request, *args, **kwargs):
        request.data.update({"post_owner" : Profile.objects.get(user = request.user).id})
        return super().post(request, *args, **kwargs)
    
    
class FeedView(views.APIView):
    
    permission_classes = [IsAuthenticated]

    def check_post_exists_in_response(self, post, response):
        for item in response:
            if post.id == item['id']:
                return True
        return False
    
    def get(self, request, *args, **kwargs):
        response = list()
        
        user_profile = get_object_or_404(Profile, user = self.request.user)
        following_profiles = self.request.user.following.all()
        for profile in following_profiles:
            
            for reaction in profile.post_reactions.all():
                if not self.check_post_exists_in_response(reaction.post,response):
                    data = PostSerializer(instance = reaction.post).data
                    data['message'] = f"{reaction.post.post_owner.full_name} reacted to this Post."
                    response.append(data)

            for comment in profile.comment_set.all():
                if not self.check_post_exists_in_response(comment.post,response):
                    data = PostSerializer(instance = comment.post).data
                    data['message'] = f"{reaction.post.post_owner.full_name} commented on this Post."
                    response.append(data)
                    
            for post in profile.created_posts.all():
                if not self.check_post_exists_in_response(post,response):
                    data = PostSerializer(instance = post).data
                    response.append(data)
                    
        for hashtag in user_profile.followed_hastags.all():
            for post in hashtag.associated_posts.filter().exclude(post_owner = user_profile):
                if not self.check_post_exists_in_response(post,response):
                    data = PostSerializer(instance = post).data
                    data['message'] = f" A post related to {hashtag.topic} "
                    response.append(data)
                    
        return Response(response, status=status.HTTP_200_OK)
    
    
  
  
class RePostView(CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    
    
    def post(self, request, *args, **kwargs):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        if request.data.get('parent_post') is None:
            return Response({"detail": "For reposting provide parent_post field"})
        request.data.update({"post_owner" : Profile.objects.get(user = request.user).id,
                             "parent_post" : request.data.get('parent_post')})
        return super().post(request, *args, **kwargs)


    
# class HashTagFollowView(ListCreateAPIView):
    
#     permission_classes = [IsAuthenticated]
#     serializer_class = HashTagFollowSerializer
    
    