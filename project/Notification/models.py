from django.db import models
from Profile.models import Profile
# Create your models here.


class NotificationType(models.Model):
    
    type = models.CharField(max_length=100)


class Notification(models.Model):
    
    type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    target  = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'received_noti')
    source  = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'sent_noti')
    created_at = models.DateTimeField(auto_now = True)
    seen = models.BooleanField(default = False)
    action = models.IntegerField()
    