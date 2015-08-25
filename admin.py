# -*- coding: utf-8 -*-
from models import *
from base import PostSaveMessageEvent
from django.contrib import admin
from django.db.models import get_model

class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'log', 'receiver')
    list_filter = ( 'receiver', )

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'message_type', 'recipient', 'to_emails', 'creation_datetime', 'sent_sucessfully', 'trigger_info')
    search_fields = ('subject',)


class PostSaveMessageEventAdmin(admin.ModelAdmin):
    list_display = ('publication_datetime', 'instance_id', 'app_label', 'model_name', 'process_lock_datetime', 'process_finished_datetime')

admin.site.register(CustomReceiver)
admin.site.register(MessageLog, MessageLogAdmin)
admin.site.register(PostSaveMessageEvent, PostSaveMessageEventAdmin)

import registry
for reg_cls in registry.classes:
    for registered_cls in reg_cls._models:
        admin.site.register(registered_cls)

