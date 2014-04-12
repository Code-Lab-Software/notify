from django import template

from django.core.exceptions import ObjectDoesNotExist
from rec.system.models import render_string

register = template.Library()

@register.filter
def interview_decision_message(decision):
    """ Renders decision template. The template is stored
    in DB via `notify.InterviewDecisionTemplate` model.

    """
    try:
        tpl_obj = decision.decision_type.interviewdecisiontemplate
        context = {'decision': decision,
                   'application': decision.get_application()}
        return render_string(tpl_obj.template, context)
    except ObjectDoesNotExist:
        return 'No decision templates message has been found.'
    except Exception, error:
        return 'Some unexptected behaviour occured. Error info: %s' % error
 