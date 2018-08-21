from . import base
from django.db.models.base import ModelBase
# -------------------------------------------------------
# Meta-stuff
# -------------------------------------------------------
class DEPMessageTypeTracker(type):
    def __new__(cls, name, bases, attrs):
        _new = super(MessageTypeTracker, cls).__new__(cls, name, bases, attrs)
        classes = set(['PostSaveMessageType'])
        message_type_class = classes.intersection(set([base.__name__ for base in bases]))
        if not message_type_class:
            return _new
        message_type_registry = message_type_class.pop()
        globals()[message_type_registry]._registry.append(_new)
        return _new

message_types = []

class MessageTypeTracker(type):
    def __new__(cls, name, bases, attrs):
        _new = super(MessageTypeTracker, cls).__new__(cls, name, bases, attrs)
        matching_bases = [base for base in bases if base.__name__.endswith('MessageType')]
        if not matching_bases:
            return _new
        if len(matching_bases) > 1:
            raise TypeError("Message configuration classes can have only one *MessageType as its base")
        # If there's only one *MessageType, register the subclass with it
        message_type = matching_bases.pop()
        message_type._registry.append(_new)
        globals()['message_types'].append(message_type)
        return _new

    
# -------------------------------------------------------
# Post-save message type
# -------------------------------------------------------
class MessageTypeBase(object):
    __metaclass__ = MessageTypeTracker
    _registry = []



