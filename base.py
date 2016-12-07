# -*- coding: utf-8 -*-
import datetime

from django.apps import apps
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import linebreaksbr

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

    def get_subject_tpl(self, instance, receiver, lang=None):
        if hasattr(self, 'get_%s_subject_tpl' % receiver):
            return getattr(self, 'get_%s_subject_tpl' % receiver)(instance, lang) or self.SUBJECT_TPL
        return self.SUBJECT_TPL

    def get_body_tpl(self, instance, receiver, lang=None):
        if hasattr(self, 'get_%s_body_tpl' % receiver):
            return getattr(self, 'get_%s_body_tpl' % receiver)(instance, lang) or self.BODY_TPL
        return self.BODY_TPL

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

    def send(self, instance, receiver):
        bcc_emails = self.get_bcc_emails()
        context = self.get_message_context(instance)

        emails_data = getattr(self, 'get_%s_emails' % receiver)(instance)

        if isinstance(emails_data, list):
            for email in emails_data:
                if email: # sometimes email is empty
                    local_context = context.copy()
                    local_context['email'] = email
                    self.notify(local_context, self.get_subject_tpl(instance, receiver), self.get_body_tpl(instance, receiver), email, bcc_emails, instance, receiver)
        if isinstance(emails_data, dict):
            for lang, emails in emails_data.keys(), emails_data.values():
                for email in emails:
                    if email: # sometimes email is empty
                        local_context = context.copy()
                        local_context['email'] = email
                        self.notify(local_context, self.get_subject_tpl(instance, receiver, lang), self.get_body_tpl(instance, receiver, lang), email, bcc_emails, instance, receiver, lang)

    def notify(self, context, subject_tpl, body_tpl, receiver_email, bcc_emails, instance, recipient, lang=None):
        subject = render_string(subject_tpl, context, lang)
        body = render_string(body_tpl, context, lang)
        email = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL,
                                       [receiver_email], bcc_emails,
                                       headers = {'Reply-To': settings.DEFAULT_FROM_EMAIL})
        email.attach_alternative(linebreaksbr(body), "text/html")
        logged_message = apps.get_model('notify', 'MessageLog').objects.create_from_email(email, self, instance, recipient, trigger_info=self.get_trigger_info(instance))

        if getattr(settings, 'NOTIFICATIONS_ENABLED', False):
            try:
                email.send()
                logged_message.sent_sucessfully = True
            except Exception, error:
                if logged_message:
                    logged_message.error_note = u"%s" % error
        logged_message.save()

    def render_body(self, instance, lang):
        context = self.get_message_context(instance)
        return render_string(self.get_body_tpl(instance, lang), context, lang)

    def render_subject(self, instance, lang):
        context = self.get_message_context(instance)
        return render_string(self.get_subject_tpl(instance, lang), context, lang)

