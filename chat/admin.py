from django.contrib import admin

# Register your models here.
from .models import ChatMessage , ChatRoom

admin.site.register(ChatRoom)
admin.site.register(ChatMessage)