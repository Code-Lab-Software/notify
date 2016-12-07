from django.apps import AppConfig

class NotifyConfig(AppConfig):
    name = 'notify'
    verbose_name = "Notify"

    def ready(self):
        #from notify import signals
        from notify import factory
        factory.register_message_models()

