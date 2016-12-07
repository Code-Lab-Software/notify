# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0004_postsavemessageevent_site_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messagelog',
            name='message_type_id',
        ),
    ]
