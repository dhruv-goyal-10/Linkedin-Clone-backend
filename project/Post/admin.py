from django.contrib import admin
from Post.models import *
# Register your models here.



admin.site.register(Post)
admin.site.register(PostReaction)
admin.site.register(Comment)
admin.site.register(CommentReaction)
admin.site.register(CommentReply)
admin.site.register(ReactionType)
admin.site.register(PostImages)
admin.site.register(ReplyReaction)
admin.site.register(HashTag)