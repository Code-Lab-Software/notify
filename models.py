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
    notification_type  = models.ForeignKey('contenttypes.ContentType')
    object_id = models.PositiveIntegerField()
    message_type = generic.GenericForeignKey('notification_type', 'object_id')
    email = models.EmailField()


def db_table_exists(table, using):
    try:
        from django.db import connections, DEFAULT_DB_ALIAS
        connection = connections[using]
        cursor = connection.cursor()
        table_names = connection.introspection.get_table_list(cursor)
    except Exception, error:
        raise Exception("unable to determine if the table '%s' exists" % table)
    else:
        return table in map(str, table_names)

try:
    message_models_factory.register_message_models()
    #if db_table_exists(FieldCacheSetup._meta.db_table, 'compose'):
    #    cached_models_factory.register_cache_models()
except Exception, error:
    print('Exception raised during the DB schema detection - field cache tables will not be created')
    print('Exception detail: %s' % error)
