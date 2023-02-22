from django.urls import path
from Profile.views import *
from Network.views import *

urlpatterns = [
    path('connection/request/send/', ConnectionRequestSendView.as_view()),
    path('connection/request/send/withdraw/<int:pk>/', ConnectionRequestWithdrawView.as_view()),
    path('connection/request/received/', ConnectionRequestReceiveView.as_view()),
    path('connection/request/received/ignore/<int:pk>/', ConnectionRequestIgnoreView.as_view()),
    path('connection/request/received/accept/', ConnectionRequestAcceptView.as_view()),
    path('connection/list/', ConnectionListView.as_view()),
    path('connection/remove/', ConnectionRemoveView.as_view()),
    path('following/', FollowingView.as_view()),
    path('following/<int:pk>/', DeleteFollowingView.as_view()),
    path('followers/', FollowersView.as_view()),
    path('connection/mutual/', MutualConnectionsView.as_view()),
    path('unfollow/', UnfollowView.as_view()),
    ]
