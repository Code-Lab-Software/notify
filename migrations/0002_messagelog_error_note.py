# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagelog',
            name='error_note',
            field=models.TextField(default='', verbose_name=b'Error note'),
            preserve_default=False,
        ),
    ]
