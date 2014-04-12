from django.db import models
from django.conf import settings

def get_model_name(registered_cls):
    return registered_cls.__name__

class MessageModelsFactory(object):

    def register_message_models(self):
        import registry
        for reg_cls in registry.classes:
            for registered_cls in reg_cls._registry:
                print('Creating message type model: %s...' % registered_cls)
                try:
                    mdl = self.create_related_model(reg_cls, registered_cls)
                    reg_cls.register_model(registered_cls, mdl)
                except Exception, error:
                    print('\t Failed... Error: %s' % error)
                else:
                    print('\t Model %s created!' % mdl)

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
        Returns a dictionary of fields that will be added to the historical
        record model, in addition to the ones returned by copy_fields below.
        """
        BASE_RECEIVERS = (('sys_manager', 'System manager'), ('sys_admin', 'System admin'), ('custom_receiver', 'Custom receivers'))
        return {'subject':  models.CharField(max_length=255, verbose_name="Notification subject template"),
                'body':  models.TextField(verbose_name="Notification body template"),
                'receiver': models.CharField(max_length=31, choices=BASE_RECEIVERS + registered_cls.RECEIVERS)
                }


