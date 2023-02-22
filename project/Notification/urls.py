from django.urls import path
from Notification.views import *

urlpatterns = [
    path('list/', NotificationView.as_view())
    ]
    
    