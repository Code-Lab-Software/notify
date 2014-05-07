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
                self.notify(context, self.subject, self.body, email, bcc_emails, self, instance, self.receiver)

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

def notify_on_post_save(sender, instance, created, raw, using, **kwargs):
    import registry
    is_created_state = ['a', 'b'] if created else ['a', 'c']
    for message_type in registry.PostSaveMessageType._models:
        for message in message_type.objects.filter(is_created_state__in=is_created_state):
            message.send(instance)
