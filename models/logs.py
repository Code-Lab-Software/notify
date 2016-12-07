# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

# -------------------------------------------------------
# Message logger
# -------------------------------------------------------

class MessageLogManager(models.Manager):
    def create_from_email(self, email, message_type, instance, recipient, trigger_info):
        message_type_pth = "%s.%s" % (self.__module__, self.__class__)
        obj = self.create(subject=email.subject,
                          body=email.body,
                          from_email=email.from_email,
                          to_emails=",".join(email.to),
                          bcc_emails=",".join(email.bcc),
                          message_type=message_type_pth,
                          trigger_info=trigger_info,
                          recipient=recipient,
                          )
        return obj

class MessageLog(models.Model):
    subject = models.CharField(max_length=512, verbose_name="Subject")
    body = models.TextField(verbose_name="Body")
    from_email = models.EmailField(verbose_name="From")
    to_emails = models.CharField(max_length=512, verbose_name="To emails")
    bcc_emails = models.CharField(max_length=512, verbose_name="BCC emails")
    creation_datetime = models.DateTimeField(auto_now_add=True, verbose_name="Sending datetime")
    sent_sucessfully = models.BooleanField(verbose_name="Sent succesfully?", default=False)    
    
    message_type = models.CharField(max_length=255) # Stores the message model name

    recipient = models.CharField(max_length=512, verbose_name="Recipient")

    trigger_info = models.CharField(max_length=255)
    error_note = models.TextField(verbose_name="Error note", default='')

    objects = MessageLogManager()


    def forward(self, to_email=None):
        email = EmailMessage(self.subject, self.body, settings.DEFAULT_FROM_EMAIL,
                             [to_email], headers = {'Reply-To': settings.DEFAULT_FROM_EMAIL})
        try:
            email.send()
        except Exception, error:
            print error


