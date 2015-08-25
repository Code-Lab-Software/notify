# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0002_messagelog_error_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagelog',
            name='error_note',
            field=models.TextField(default=b'', verbose_name=b'Error note'),
            preserve_default=True,
        ),
    ]
