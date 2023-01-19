from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ConnectionRequest)
admin.site.register(FirstConnections)
admin.site.register(SecondConnections)
admin.site.register(Follow)