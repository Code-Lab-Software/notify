# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomReceiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('email', models.EmailField(max_length=75)),
                ('notification_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=512, verbose_name=b'Subject')),
                ('body', models.TextField(verbose_name=b'Body')),
                ('from_email', models.EmailField(max_length=75, verbose_name=b'From')),
                ('to_emails', models.CharField(max_length=512, verbose_name=b'To emails')),
                ('bcc_emails', models.CharField(max_length=512, verbose_name=b'BCC emails')),
                ('creation_datetime', models.DateTimeField(auto_now_add=True, verbose_name=b'Sending datetime')),
                ('sent_sucessfully', models.BooleanField(default=False, verbose_name=b'Sent succesfully?')),
                ('message_type', models.CharField(max_length=255)),
                ('message_type_id', models.PositiveIntegerField()),
                ('recipient', models.CharField(max_length=512, verbose_name=b'Recipient')),
                ('trigger_info', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostSaveMessageEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance_id', models.PositiveSmallIntegerField()),
                ('app_label', models.CharField(max_length=127)),
                ('model_name', models.CharField(max_length=127)),
                ('event_mode', models.CharField(max_length=1, choices=[(b'c', b'Created'), (b'u', b'Updated'), (b'd', b'Deleted')])),
                ('publication_datetime', models.DateTimeField(auto_now_add=True)),
                ('process_lock_datetime', models.DateTimeField(null=True)),
                ('process_finished_datetime', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
