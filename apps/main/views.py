from cms.models import ContentBlock
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect as redirect, HttpResponse as response, Http404

from django.utils import simplejson as json

from people.models import GenericParty
from main.models import Bubble, BubbleMenu
from do.models import Task
from django import forms

#TODO: Maybe move this too
#from pos.forms import BeverageSaleForm

def main_cms(request):
    pass

def main_landing(request):
    ''''
    TODO: Bring this back for a menu-driven front page.
    '''
    disable_incoming_calls = True
    blog_blocks = ContentBlock.objects.filter(published=True, tags__name__in=["public","blog"]).order_by('-created').distinct() [:4]           
    return render(request, "main/main_landing.html", locals())


#If the user is logging in on the front page, they have new bubbles coming their way.
def loggedInBubbles(request):
    #Which menu are we rendering?  TODO: Un-hardcode menu reference.  (For that matter, we prolly oughta take members to a completely different function)
    initial_menu = BubbleMenu.objects.get(launch_name="admin_main")

    #Get the menu tree for this menu - this will recursively get the sub-menus of its bubbles.
    menu_tree=initial_menu.getMenuTree()    
    
    #Tell the template that we want this menu to be first.
    initial_menu.first = True
        
        
#TODO: Move all of this stuff to an admin-only function.
    
    #Get the last 10 sales for display in the POS.
    from products.models import BeverageInstance
    sales=BeverageInstance.objects.order_by('created')[:10].reverse()
    
    
    '''
    The following is heavily borrowed from (and probably rightly belongs in) hwtrack.views.
    I'm putting it here mostly for testing.
    Since it's here, it doesn't need to load via ajax.
    It's probably best to re-ajax it.
    -Justin
    '''
    from hwtrack.models import Device
#    from service.models import RenderDeviceService
    from people.models import Client
    
    class AddClientForm(forms.ModelForm):
        class Meta:
            model=Client
    
    class AddDeviceForm(forms.ModelForm):
        class Meta:
            model=Device
            

            
#    class AddServiceForm(forms.ModelForm):
#        class Meta:
#            model=RenderDeviceService
    
    service_check_in_forms=(AddClientForm(), AddDeviceForm())
    
    
#END AREA OF ADMIN-ONLY STUFF
    
    return render('main/logged_in_bubbles.html', locals())

def rightSideWidgets(request):
    from django.contrib.sessions.models import Session
    from django.contrib.auth.models import User
    
    user_ids = []
    
    for session in Session.objects.all():
        try:
            id = session.get_decoded()['_auth_user_id']
            user_ids.append(id)
        except KeyError:
            pass
    
    
    tasks = Task.objects.filter_active_by_owner(request.user)
    
    logged_in_users = User.objects.filter(id__in=user_ids).distinct()
    
    #TODO: This needs to be all the widgets, not just whoisloggedin
    return render('widgets/whoIsLoggedIn.html', locals() )  


def hack_and_tell(request):
    
    return render(request,'main/hack_and_tell/info.html', locals())

def moving(request):
    moving_content_blocks = ContentBlock.objects.filter(tags__name='moving_2012_blocks')
    invisible_footer = True
    return render(request, 'main/moving.html', locals())