# -*- coding: utf-8 -*-
from .models import *
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'log', 'receiver')
    list_filter = ( 'receiver', )

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'message_type', 'recipient', 'to_emails', 'creation_datetime', 'sent_sucessfully', 'trigger_info')
    search_fields = ('subject',)


class PostSaveMessageEventAdmin(admin.ModelAdmin):
    list_display = ('publication_datetime', 'instance_id', 'app_label', 'model_name', 'process_lock_datetime', 'process_finished_datetime',
                    'site_id', 'event_mode')

admin.site.register(MessageLog, MessageLogAdmin)
admin.site.register(PostSaveMessageEvent, PostSaveMessageEventAdmin)


