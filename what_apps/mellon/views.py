from .models import MagneticCard
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from what_apps.presence.models import LocationStatePrototype
from what_apps.presence.views import open_slashroot
from what_apps.push.functions import push_with_template
import hashlib

def read_card(card_string):
    '''
    takes a raw card string and returns a tuple where:
    the first value is True or False for success 
    second value is either a hash or 0 for blank, 1 for read error  
    '''
    card_read_error = bool(card_string[1:3] == "E?" )
    if not (not card_string or card_read_error): #success branch
         hashed_stripstring = hashlib.sha1(card_string).hexdigest()
         return (True, hashed_stripstring) 
    else: #error branch
        if not card_string:
            return (False, 0)
        if card_read_error:
            return (False, 1)
    
def save_new_card(request):
    ''' 
    after user presses the save button in the form this magneticCard will be assigned to them
    '''
    if request.POST:
        try:
            (success, data) = read_card(request.POST['rawString'])#unpacking the tuple, if success then we have a hash called data
            if success:
                hashed_stripstring = data #since success is true we know that read_data returned hash for its second value which we have named data above. 
                
                MagneticCard.objects.create(owner = request.user, hash = hashed_stripstring)
                messages.success(request, "Thank You. Your Card Has Been Saved!")
                return HttpResponseRedirect("/do/")
            else: 
                #success is false so data is not a hash, data is 0 or 1
                if data == 0:
                    messages.error(request, "No Card Detected")
                if data == 1:
                    messages.error(request, "Swipe Error or Bunk Card")
                return render(request,"mellon/new_card_function_form.html") 
        except MultiValueDictKeyError:
            # send them back to the form
            pass
    
        
@login_required        
def new_card_function_form(request):
    return render(request,"mellon/new_card_function_form.html")

def authenticate_card(request):
    '''
    this is the logic on the server that handles the card swipe into the field
    '''
    if not request.META['REMOTE_ADDR'] == '10.0.0.175': #TODO: uncoment for production
        return HttpResponseForbidden()

    
    
    (success, data) = read_card(request.POST['rawString']) 
    if success:
        try:
            card = MagneticCard.objects.get(hash = data)
            user = card.owner
            user.backend = 'django.contrib.auth.backends.ModelBackend' #a little hackey, but suggested by http://stackoverflow.com/questions/2787650/manually-logging-in-a-user-without-password
            
            login(request, user)
            
            if LocationState.objects.latest('created').name == 'closed':
                push_with_template('do/do_feed_items/login_swipe', {'item': user, 'opening':True}, "/feeds/do/llamas/walruses/activity") #TODO: Make this better.
                open_slashroot(request)
            else:
                push_with_template('do/do_feed_items/login_swipe', {'item': user}, "/feeds/do/llamas/walruses/activity") #TODO: Make this better.
            
            return HttpResponse(1)
        except MagneticCard.DoesNotExist:
            pass
        
        

  