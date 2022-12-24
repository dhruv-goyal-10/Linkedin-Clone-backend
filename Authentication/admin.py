from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  
  list_display = ('email','created_at', 'is_admin', 'is_active')
  list_filter = ('is_admin','is_active',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password')}),
      ('Personal info', {'fields': ('created_at',)}),
      ('Permissions', {'fields': ('is_admin','is_active')}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  
  add_fieldsets = (
    
      ("Hello!", {
          'classes': ('wide',),
          'fields': ('email','password1', 'password2'),
      }),
  )
  search_fields = ('email','phone_number','created_at')
  ordering = ('email',)
  filter_horizontal = ()


class EmailOTPModelAdmin(admin.ModelAdmin):
  list_display = ('email', 'otp','otp_created_at')
  fieldsets = (
      ('Details', {'fields': ('email', 'otp',)}),
  )
  
class PhoneOTPModelAdmin(admin.ModelAdmin):
  list_display = ('phone_number', 'otp','otp_created_at')

admin.site.register(User, UserModelAdmin)
admin.site.register(PhoneOTP, PhoneOTPModelAdmin)
admin.site.register(EmailOTP, EmailOTPModelAdmin)