"""Message template models factory - inspired by Marty Alchin recipe for django-simple-history"""

def get_model_name(msg_config):
    """Returns the name of dynamically created message model."""
    return msg_config.__name__

def get_message_fields(msg_config):
    """
    Returns a dictionary of fields that will be added to the message template model.
    Every message template class will have:
     - message subject,
     - message body,
     - receiver type,
    """
    return {'SUBJECT_TPL':  msg_config.SUBJECT_TPL,
            'BODY_TPL':  msg_config.BODY_TPL,
            'RECEIVERS': msg_config.RECEIVERS,}

def create_related_model(msg_type, msg_config):
    """
    Creates a message model to associate with the registered_cls provided.
    """
    attrs = {'__module__': 'notify.models'}
    attrs.update(get_message_fields(msg_config))
    name = get_model_name(msg_config)
    return type(name, (msg_type.base_model, msg_config.Receivers), attrs)


def register_message_models():
    """Creates and registers dynamic message model, which is based
    on message type and its configuration classes."""
    from notify import registry
    for msg_type in registry.message_types:
        for msg_config in msg_type._registry:
            msg_model = create_related_model(msg_type, msg_config)
            msg_type.register_model(msg_config, msg_model)
