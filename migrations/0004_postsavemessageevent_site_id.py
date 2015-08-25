# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0003_auto_20150825_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='postsavemessageevent',
            name='site_id',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
