# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0005_remove_messagelog_message_type_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customreceiver',
            name='notification_type',
        ),
        migrations.DeleteModel(
            name='CustomReceiver',
        ),
        migrations.AlterField(
            model_name='postsavemessageevent',
            name='event_mode',
            field=models.CharField(max_length=1, choices=[(b'c', b'Created'), (b'u', b'Updated')]),
            preserve_default=True,
        ),
    ]
