from django.template import Library
from django.template.loader import get_template
from comm.models import PhoneCall
from django.template.context import Context
from service.models import Service
from django.core.cache import cache
from private import resources
from django.template.base import Node

register = Library()

class NavigationBar(Node):
    
    def __init__(self, parser, token):
        #Handle parser and token.
        super(NavigationBar, self).__init__()
    
    def render(self, context):
        template = get_template('global_nav.html')
        
        cached_calls = cache.get('number_of_unresolved_calls')
        unresolved_calls = cached_calls or PhoneCall.objects.unresolved().count()
        if not cached_calls:    
            cache.set('number_of_unresolved_calls', unresolved_calls, 600)
        
        cached_tech_jobs = cache.get('number_of_tech_needing_attention') 
        tech_jobs = cached_tech_jobs or len(Service.objects.filter_by_needing_attention()[0])
        if not cached_tech_jobs:
            cache.set('number_of_tech_needing_attention', tech_jobs, 600)
        
        context['calls'] = unresolved_calls
        context['tech_jobs'] = tech_jobs
        context['pos_url'] = resources.POS_URL
        
        return template.render(context)


register.tag('navigation_bar', NavigationBar)