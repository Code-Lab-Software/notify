# -*- coding: utf-8 -*-
import datetime

from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import get_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils import translation
from django import template

def render_string(content, context, lang=None):
    default_lang = translation.get_language()
    trans_lang = lang or default_lang
    translation.activate(trans_lang)
    output = template.Template(content).render(template.Context(context))
    translation.activate(default_lang)
    return output

# -----------------------------------------
# Base message-sending logic
# -----------------------------------------

class MessageMixin(object):

    def get_subject_tpl(self, instance, lang=None):
        if hasattr(self, 'get_%s_subject_tpl' % self.receiver):
            return getattr(self, 'get_%s_subject_tpl' % self.receiver)(instance, lang) or self.subject
        return self.subject

    def get_body_tpl(self, instance, lang=None):
        if hasattr(self, 'get_%s_body_tpl' % self.receiver):
            return getattr(self, 'get_%s_body_tpl' % self.receiver)(instance, lang) or self.body
        return self.body

    def get_sys_manager_emails(self, instance):
        return map(lambda x: x[1], settings.MANAGERS) 

    def get_sys_admin_emails(self, instance):
        return  map(lambda x: x[1], settings.ADMINS) 

    def get_custom_receiver_emails(self, instance):
        return  self.custom_receivers.values_list('email', flat=True)

    def get_bcc_emails(self):
        # do przemyslenia opcjonalna obsluga 
        # wysylania BCC na mejla servera wysylajcaego
        #return [settings.DEFAULT_FROM_EMAIL]
        return []

    def get_message_context(self, instance):
        return {'instance': instance}

    def send(self, instance):
        bcc_emails = self.get_bcc_emails()
        context = self.get_message_context(instance)

        emails_data = getattr(self, 'get_%s_emails' % self.receiver)(instance)

        if isinstance(emails_data, list):
            for email in emails_data:
                if email: # sometimes email is empty
                    self.notify(context, self.get_subject_tpl(instance), self.get_body_tpl(instance), email, bcc_emails, self, instance, self.receiver)
        if isinstance(emails_data, dict):
            for lang, emails in emails_data.keys(), emails_data.values():
                for email in emails:
                    if email: # sometimes email is empty
                        self.notify(context, self.get_subject_tpl(instance, lang), self.get_body_tpl(instance, lang), email, bcc_emails, self, instance, self.receiver, lang)

    def notify(self, context, subject_tpl, body_tpl, receiver_email, bcc_emails, message_type, instance, recipient, lang=None):
        subject = render_string(subject_tpl, context, lang)
        body = render_string(body_tpl, context, lang)
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL,
                             [receiver_email], bcc_emails,
                             headers = {'Reply-To': settings.DEFAULT_FROM_EMAIL})
        logged_message = None

        if self.is_archived:
            logged_message = get_model('notify', 'MessageLog').objects.create_from_email(email, message_type, instance, recipient, trigger_info=self.get_trigger_info(instance))

        if getattr(settings, 'NOTIFICATIONS_ENABLED', False):
            try:
                email.send()
                if logged_message:
                    logged_message.sent_sucessfully = True
                    logged_message.save()
            except Exception, error:
                if logged_message:
                    print 'Error:', error
                    logged_message.error_note = u"%s" % error
                    logged_message.save()

    def render_body(self, instance, lang):
        context = self.get_message_context(instance)
        return render_string(self.get_body_tpl(instance, lang), context, lang)

    def render_subject(self, instance, lang):
        context = self.get_message_context(instance)
        return render_string(self.get_subject_tpl(instance, lang), context, lang)

# -----------------------------------------
# Post-save signal handler
# -----------------------------------------
class PostSaveMessage(models.Model, MessageMixin):
    is_created_state = models.CharField(max_length=1, choices=(('a', 'Any'), ('b', 'On creation only'), ('c', 'On update only')))

    def get_trigger_info(self, instance):
        return "%s.%s.%s" % (instance._meta.app_label, instance._meta.object_name, instance.pk)

    @classmethod
    def register_model(cls, registered_cls, mdl):
        for m in registered_cls.MODELS:
            post_save.connect(notify_on_post_save, sender=m)

    class Meta:
        abstract = True


class PostSaveMessageEventManager(models.Manager):

    def create_from_instance(self, instance, created):
        import registry
        for message_type in registry.PostSaveMessageType._models:
            if instance.__class__ in registry.PostSaveMessageType._models[message_type]:
                self.create(instance_id=instance.id,
                            site_id=getattr(settings, 'SITE_ID'),
                            app_label=instance._meta.app_label,
                            model_name=instance._meta.object_name.lower(),
                            event_mode='c' if created else 'u')
                # jeżeli znalazłem już jakiś zgodny wpis, nie szukam dalej
                break

    def process_events(self):
        pending_events = self.filter(process_lock_datetime__isnull=True, site_id=getattr(settings, 'SITE_ID'))
        pending_events_ids = list(pending_events.values_list('id', flat=True))
        print('Pozostało %d obiektów do przetworzenia.' % pending_events.count())
        # Blokuję przetwarzanie
        pending_events.update(process_lock_datetime=datetime.datetime.now())
        for event in self.filter(id__in=pending_events_ids):
            self.process_event(event)

    def process_event(self, event):
        if event.process_finished_datetime:
            return
        import registry
        # Jeżeli event nie jest jeszcze oznaczony jako przetwarzany
        # to go oznaczamy
        if event.process_lock_datetime is None:
            event.process_lock_datetime = datetime.datetime.now()
            event.save()
        # Przetwarzamy event
        created = event.event_mode == 'c'
        instance = event.get_instance()
        if not instance is None:
            is_created_state = ['a', 'b'] if created else ['a', 'c']
            for message_type in registry.PostSaveMessageType._models:
                if instance.__class__ in registry.PostSaveMessageType._models[message_type]:
                    for message in message_type.objects.filter(is_created_state__in=is_created_state):
                        message.send(instance)
        # Oznaczamy event jako przetworzony
        event.process_finished_datetime = datetime.datetime.now()
        event.save()

class PostSaveMessageEvent(models.Model):
    instance_id = models.PositiveSmallIntegerField()
    site_id = models.PositiveSmallIntegerField()
    app_label = models.CharField(max_length=127)
    model_name = models.CharField(max_length=127)
    event_mode = models.CharField(max_length=1, choices=(('c', 'Created'), ('u', 'Updated'), ('d', 'Deleted')))
    publication_datetime = models.DateTimeField(auto_now_add=True)
    process_lock_datetime = models.DateTimeField(null=True)
    process_finished_datetime = models.DateTimeField(null=True)

    objects = PostSaveMessageEventManager()

    def get_instance(self):
        try:
            return models.get_model(self.app_label, self.model_name).objects.get(id=self.instance_id)
        except:
            return None

def notify_on_post_save(sender, instance, created, raw, using, **kwargs):
    if getattr(settings, 'NOTIFICATIONS_ENABLED', False) and hasattr(settings, 'SITE_ID'):
        models.get_model('notify', 'PostSaveMessageEvent').objects.create_from_instance(instance, created)

# ----------------------------------------------------
# Stary mechanizm - wysłanie w czasie rzeczywistym
# do wyrzucenia wkrótce
# ----------------------------------------------------
def _notify_on_post_save(sender, instance, created, raw, using, **kwargs):
    import registry
    is_created_state = ['a', 'b'] if created else ['a', 'c']
    for message_type in registry.PostSaveMessageType._models:
        if sender in registry.PostSaveMessageType._models[message_type]:
            for message in message_type.objects.filter(is_created_state__in=is_created_state):
                message.send(instance)
