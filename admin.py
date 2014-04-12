# -*- coding: utf-8 -*-
from models import *
from django.contrib import admin
from django.db.models import get_model

class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'log', 'receiver')
    list_filter = ( 'receiver', )

admin.site.register(CustomReceiver)

import registry
for reg_cls in registry.classes:
    for registered_cls in reg_cls._models:
        admin.site.register(registered_cls)

