import datetime

from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import get_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from django import template
def render_string(content, context):
    return template.Template(content).render(template.Context(context))

# -----------------------------------------
# Base message-sending logic
# -----------------------------------------

class MessageMixin(object):

    def get_subject_tpl(self, instance):
        if hasattr(self, 'get_%s_subject_tpl' % self.receiver):
            return getattr(self, 'get_%s_subject_tpl' % self.receiver)(instance) or self.subject
        return self.subject

    def get_body_tpl(self, instance):
        if hasattr(self, 'get_%s_body_tpl' % self.receiver):
            return getattr(self, 'get_%s_body_tpl' % self.receiver)(instance) or self.body
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
        for email in getattr(self, 'get_%s_emails' % self.receiver)(instance):
            if email: # sometimes email is empty
                self.notify(context, self.get_subject_tpl(instance), self.get_body_tpl(instance), email, bcc_emails, self, instance, self.receiver)

    def notify(self, context, subject_tpl, body_tpl, receiver_email, bcc_emails, message_type, instance, recipient):
        subject = render_string(subject_tpl, context)
        body = render_string(body_tpl, context)
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL,
                             [receiver_email], bcc_emails,
                             headers = {'Reply-To': settings.DEFAULT_FROM_EMAIL})
        logged_message = None

        if self.is_archived:
            logged_message = get_model('notify','MessageLog').objects.create_from_email(email, message_type, instance, recipient, trigger_info=self.get_trigger_info(instance))

        if getattr(settings, 'NOTIFICATIONS_ENABLED', False):
            try:
                email.send()
                if logged_message:
                    logged_message.sent_sucessfully = True
                    logged_message.save()
            except Exception, error:
                if logged_message:
                    logged_message.note = u"%s" % error
                    logged_message.save()

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
                            app_label=instance._meta.app_label,
                            model_name=instance._meta.object_name.lower(),
                            event_mode='c' if created else 'u')
                # jeżeli znalazłem już jakiś zgodny wpis, nie szukam dalej
                break

    def process_events(self):
        pending_events = self.filter(process_lock_datetime__isnull=True)
        # Blokuję przetwarzanie
        pending_events.update(process_lock_datetime=datetime.datetime.now())
        for event in pending_events:
            instance = event.get_instance()
            if not instance is None:


    def process_event(self, event):
        import registry
        created = event.event_mode == 'c'
        instance = event.get_instance()
        if not instance is None:
            is_created_state = ['a', 'b'] if created else ['a', 'c']
            for message_type in registry.PostSaveMessageType._models:
                if instance.__class__ in registry.PostSaveMessageType._models[message_type]:
                    for message in message_type.objects.filter(is_created_state__in=is_created_state):
                        message.send(instance)
        event.process_finished_datetime = datetime.datetime.now()
        event.save()
        

class PostSaveMessageEvent(models.Model):
    instance_id = models.PositiveSmallIntegerField()
    app_label = models.CharField()
    model_name = models.CharField()
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
    models.get_model('notify', 'PostSaveMessageEvent').objects.create_from_instance(instance, created)

def _notify_on_post_save(sender, instance, created, raw, using, **kwargs):
    import registry
    is_created_state = ['a', 'b'] if created else ['a', 'c']
    for message_type in registry.PostSaveMessageType._models:
        if sender in registry.PostSaveMessageType._models[message_type]:
            for message in message_type.objects.filter(is_created_state__in=is_created_state):
                message.send(instance)
