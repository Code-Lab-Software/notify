import base
from django.db.models.base import ModelBase
# -------------------------------------------------------
# Meta-stuff
# -------------------------------------------------------
class MessageTypeTracker(type):
    def __new__(cls, name, bases, attrs):
        _new = super(MessageTypeTracker, cls).__new__(cls, name, bases, attrs)
        classes = set(['PostSaveMessageType'])
        message_type_class = classes.intersection(set([base.__name__ for base in bases]))
        if not message_type_class:
            return _new
        message_type_registry = message_type_class.pop()
        globals()[message_type_registry]._registry.append(_new)
        return _new

# -------------------------------------------------------
# Post-save message type
# -------------------------------------------------------
class PostSaveMessageType(object):
    base_model = base.PostSaveMessage
    __metaclass__ = MessageTypeTracker
    _registry = []
    _models = []

    @classmethod
    def register_model(cls, registered_cls, mdl):
        cls._models.append(mdl)
        cls.base_model.register_model(registered_cls, mdl)

# -------------------------------------------------------
# Other stuff
# -------------------------------------------------------
classes = [PostSaveMessageType, ]
