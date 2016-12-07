# -*- coding: utf-8 -*-
import datetime

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from notify.base import MessageMixin
from notify.registry import MessageTypeBase

# -----------------------------------------
# Message type definition
# -----------------------------------------

class PostSaveMessage(MessageMixin):

    def get_trigger_info(self, instance):
        return "%s.%s.%s" % (instance._meta.app_label, instance._meta.object_name, instance.pk)

    @classmethod
    def register_model(cls, msg_config, msg_model):
        for snd in msg_config.SENDERS:
            post_save.connect(notify_on_post_save, sender=snd)

    class Meta:
        abstract = True


class PostSaveMessageType(MessageTypeBase):
    base_model = PostSaveMessage
    _models = {}

    @classmethod
    def register_model(cls, msg_config, msg_model):
        cls._models[msg_model] = [sender.lower() for sender in msg_config.SENDERS]
        cls.base_model.register_model(msg_config, msg_model)

# -----------------------------------------
# Events storage
# -----------------------------------------
        
class PostSaveMessageEventManager(models.Manager):

    def create_from_instance(self, instance, created):
        for msg_model in PostSaveMessageType._models:
            class_name = "%s.%s" % (instance._meta.app_label, instance._meta.object_name.lower())
            if class_name in PostSaveMessageType._models[msg_model]:
                self.create(instance_id=instance.id,
                            site_id=getattr(settings, 'SITE_ID'),
                            app_label=instance._meta.app_label,
                            model_name=instance._meta.object_name.lower(),
                            event_mode='c' if created else 'u')
                # break, if any match has been already founded
                break

    def process_events(self):
        pending_events = self.filter(process_lock_datetime__isnull=True, site_id=getattr(settings, 'SITE_ID'))
        pending_events_ids = list(pending_events.values_list('id', flat=True))
        # Blokuję przetwarzanie
        pending_events.update(process_lock_datetime=datetime.datetime.now())
        for event in self.filter(id__in=pending_events_ids):
            self.process_event(event)

    def process_event(self, event):
        if event.process_finished_datetime:
            return
        # Jeżeli event nie jest jeszcze oznaczony jako przetwarzany
        # to go oznaczamy
        if event.process_lock_datetime is None:
            event.process_lock_datetime = datetime.datetime.now()
            event.save()
        # Przetwarzamy event
        created = event.event_mode == 'c'
        instance = event.get_instance()
        if not instance is None:
            is_created_state = ['any', 'create'] if created else ['any', 'update']
            for msg_model in PostSaveMessageType._models:
                class_name = "%s.%s" % (instance._meta.app_label, instance._meta.object_name.lower())
                if class_name in PostSaveMessageType._models[msg_model]:
                    for receiver in msg_model.RECEIVERS:
                        if msg_model.RECEIVERS.get(receiver) in is_created_state:
                            msg_model().send(instance, receiver)

        # Oznaczamy event jako przetworzony
        event.process_finished_datetime = datetime.datetime.now()
        event.save()

class PostSaveMessageEvent(models.Model):
    instance_id = models.PositiveSmallIntegerField()
    site_id = models.PositiveSmallIntegerField()
    app_label = models.CharField(max_length=127)
    model_name = models.CharField(max_length=127)
    event_mode = models.CharField(max_length=1, choices=(('c', 'Created'), ('u', 'Updated')))
    publication_datetime = models.DateTimeField(auto_now_add=True)
    process_lock_datetime = models.DateTimeField(null=True)
    process_finished_datetime = models.DateTimeField(null=True)

    objects = PostSaveMessageEventManager()

    def get_instance(self):
        try:
            return apps.get_model(self.app_label, self.model_name).objects.get(id=self.instance_id)
        except:
            return None

def notify_on_post_save(sender, instance, created, raw, using, **kwargs):
    if getattr(settings, 'NOTIFICATIONS_ENABLED', False) and hasattr(settings, 'SITE_ID'):
        apps.get_model('notify', 'PostSaveMessageEvent').objects.create_from_instance(instance, created)


        
