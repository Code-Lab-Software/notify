# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db.models import get_model, Q, ObjectDoesNotExist
from optparse import OptionParser, make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option("-e", "--event_type", dest="event_type"),)

    def handle(self, *args, **options):
        get_model('notify', '%smessageevent' % options.get('event_type')).objects.process_events()
