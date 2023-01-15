from django.contrib import admin
from .models import *


admin.site.register(Profile)

admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Course)
admin.site.register(TestScore)
admin.site.register(Skill)
admin.site.register(Organization)
admin.site.register(Employment)
admin.site.register(MainProfile)
admin.site.register(ProfileView)