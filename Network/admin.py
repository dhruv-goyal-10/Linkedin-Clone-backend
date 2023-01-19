from django.contrib import admin
from .models import *
# Register your models here.


class ConnectionRequestModelAdmin(admin.ModelAdmin):
  list_display = ('sender', 'reciever', 'state', 'created_at')
class FirstConnectionsModelAdmin(admin.ModelAdmin):
  list_display = ('owner', 'person')
  
class SecondConnectionsModelAdmin(admin.ModelAdmin):
  list_display = ('owner', 'person', 'count')

class ThirdConnectionsModelAdmin(admin.ModelAdmin):
  list_display = ('owner', 'person', 'count')


admin.site.register(ConnectionRequest, ConnectionRequestModelAdmin)
admin.site.register(FirstConnections, FirstConnectionsModelAdmin)
admin.site.register(SecondConnections, SecondConnectionsModelAdmin)
admin.site.register(ThirdConnections, ThirdConnectionsModelAdmin)

admin.site.register(Follow)