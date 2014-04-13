# -*- coding: utf-8 -*-
from models import *
from django.contrib import admin
from django.db.models import get_model

class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'log', 'receiver')
    list_filter = ( 'receiver', )

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'message_type', 'recipient', 'to_emails', 'creation_datetime', 'sent_sucessfully', 'trigger_info')
    search_fields = ('subject',)

admin.site.register(CustomReceiver)
admin.site.register(MessageLog, MessageLogAdmin)

import registry
for reg_cls in registry.classes:
    for registered_cls in reg_cls._models:
        admin.site.register(registered_cls)

