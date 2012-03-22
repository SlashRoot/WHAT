from django.template import Library, Template, Context
from django.template.loader import get_template

from social.forms import DrawAttentionAjaxForm
from social.models import message_threads_for_object_family as mtof

register = Library()

@register.filter
def draw_attention(object):
    t = get_template('social/draw_attention_ajax_form.html')
    
    form = DrawAttentionAjaxForm()
    
    form.fields['app'].initial = str(object._meta).split('.')[0]
    form.fields['model'].initial = str(object._meta).split('.')[1]
    form.fields['object_id'].initial = object.id
    
    c = {"form" : form}
    return t.render(Context(c))

@register.filter
def draw_attention_report(object):
    t = get_template('social/draw_attention_report_brief.html')
    c = {"object" : object}
    return t.render(Context(c))

@register.filter
def message_threads_for_object_family(object):
    return mtof(object)
    