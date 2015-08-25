# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from notify import factory
message_models_factory = factory.MessageModelsFactory()

# -------------------------------------------------------
# Custom setup models
# -------------------------------------------------------
class CustomReceiver(models.Model):
    """ Represents custom e-mail receivers. Each message type can have 
    a custom e-mail addreses registered and this model stores that addreses.
    """

    notification_type  = models.ForeignKey('contenttypes.ContentType')
    object_id = models.PositiveIntegerField()
    message_type = generic.GenericForeignKey('notification_type', 'object_id')
    email = models.EmailField()

# -------------------------------------------------------
# Message logger
# -------------------------------------------------------

class MessageLogManager(models.Manager):
    def create_from_email(self, email, message_type, instance, recipient, trigger_info):
        message_type_pth = "%s.%s" % (message_type._meta.app_label, message_type._meta.object_name)
        obj = self.create(subject=email.subject,
                          body=email.body,
                          from_email=email.from_email,
                          to_emails=",".join(email.to),
                          bcc_emails=",".join(email.bcc),
                          message_type=message_type_pth,
                          message_type_id=message_type.id,
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
    
    # It might be a tempting idea to store the `message_type` as a ContentType... 
    # But in case of content_type removal, CharField will keep the information about the 
    # message type that was used to render the triggered email.
    message_type = models.CharField(max_length=255)
    message_type_id = models.PositiveIntegerField()

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


# -------------------------------------------------------
# Message-templates factory
# -------------------------------------------------------

# Scan registered types and create related message-models. For details
# see `notify.factory`.
try:
    message_models_factory.register_message_models()
except Exception, error:
    print('Exception raised during the message models creation!')
    print('Exception detail: %s' % error)
