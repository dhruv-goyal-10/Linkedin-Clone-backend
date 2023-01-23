from rest_framework import status
from rest_framework.generics import *
from Notification.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from itertools import chain
from Post.views import BasicPagination
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination



class NotificationView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = BasicPagination
    
    def get_queryset(self):
        profile = get_object_or_404(Profile, user = self.request.user)
        queryset = Notification.objects.filter(target = profile).order_by('-created_at')
        self.request.data.update({'unseen_notification_count' : queryset.filter(seen = False).count()})
        return queryset

    def get(self, request, *args, **kwargs):
        response =  super().get(request, *args, **kwargs)
        response.data['unseen_notification_count'] = request.data['unseen_notification_count']
        return response
        