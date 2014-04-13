""" 
Message template models factory - based on the Marty Alchin recipe for django-simple-history
"""

from django.db import models
from django.conf import settings

def get_model_name(registered_cls):
    return registered_cls.__name__

class MessageModelsFactory(object):
    """ This is a factory class - it will dynamically create
        message-type models using the information stored in 
        the registry classes list in `registry.classes`.

    """

    def register_message_models(self):
        import registry
        for reg_cls in registry.classes:
            for registered_cls in reg_cls._registry:
                try:
                    mdl = self.create_related_model(reg_cls, registered_cls)
                    reg_cls.register_model(registered_cls, mdl)
                except Exception, error:
                    print('\t Dynamic model creation for %sfailed... Error: %s' % (registered_cls, error))

    def create_related_model(self, reg_cls, registered_cls):
        """
        Creates a message model to associate with the registered_cls provided.
        """
        attrs = {'__module__': 'notify.models'}
        attrs.update(self.get_message_fields(registered_cls))
        name = get_model_name(registered_cls)
        return type(name, (reg_cls.base_model, registered_cls.Receivers), attrs)

    def get_message_fields(self, registered_cls):
        """
        Returns a dictionary of fields that will be added to the message template model.
        Every message template class will have:
         - message subject,
         - message body,
         - receiver type,
         - is_archived flag .
        
        """
        BASE_RECEIVERS = (('sys_manager', 'System manager'), ('sys_admin', 'System admin'), ('custom_receiver', 'Custom receivers'))
        return {'subject':  models.CharField(max_length=255, verbose_name="Notification subject template"),
                'body':  models.TextField(verbose_name="Notification body template"),
                'receiver': models.CharField(max_length=31, choices=BASE_RECEIVERS + registered_cls.RECEIVERS),
                'is_archived': models.BooleanField(verbose_name="Archive sent emails?", default=False)
                }


