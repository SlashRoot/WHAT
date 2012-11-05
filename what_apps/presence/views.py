from .models import LocationStatePrototype, Location, PresenceInstance, \
    PresencePurpose, AnchorTime
from django import forms
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.http import HttpResponse as response, HttpResponse
from django.shortcuts import render_to_response as render
import datetime
import json
import os



def whoIsHere():
    
    logged_in = []
    for s in Session.objects.all():
        try:
            logged_in.append(s.get_decoded()['presence'])
        except:
            pass

    return logged_in


def askPurpose(request):
    '''
    The user is a member and they are inside the walls.  Why are they here?
    '''
    class PresenceForm(forms.ModelForm):
        class Meta:
            model = PresenceInstance
            exclude = ['member']
    
    form = PresenceForm()
    
    return render('askPurpose.html', locals())

def tellPurpose(request):
    '''
    The member is telling us why they are here.
    '''
    
    try:
        user = request.session['member'] #We saved the user in session; now we'll log them in.
        login(request, user) #We have the user because they are already logged in.
    except KeyError:
        user = request.user
    
    
    
    
    member = user.everyone.member
    purpose_id=request.POST['purpose']
    purpose=PresencePurpose.objects.get(id=purpose_id)
    presence=PresenceInstance(member=member, purpose=purpose)
    presence.save()
    
    request.session['presence'] = presence
    
    
    
    return response(json.dumps(1))


def getAnchorsByDate(date):
    '''
    This function returns a list of AnchorTime objects for a particular date.
    '''
    dow = datetime.date.weekday(date)
    anchors = AnchorTime.objects.filter(dow=dow)
    return anchors





#Stupidly simple login function.  Check the credentials, return 1 for success, 0 for no success.
#Obviously the expectation is that we're using ajax / json for this.
def bareLogin(request):
    username = request.POST['username']
    password = request.POST['password']
    
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            
            logged = 1  #They exist and they are active. We're surely going to log this person in, one way or another. 
            
            try:
                if user.everyone.member:
                    top_level=request.META['REMOTE_ADDR'].split('.')[0] #Split the user's IP address. 
                    if True: #temp: top_level == str(10): #If the first number of the IP address is 10.....
                        logged=2  #Send a signal that the user is a member and is in the store.
                        request.session['member']=user #Save this user in session, but do not log them in yet.
                    else:
                        login(request, user) #They are a member, but not in the store.  Log them in.
            except AttributeError:
                login(request, user) #They aren't a member, but they entered good creds.  Log them in.
        
        else:
            logged = 0
    else:
        logged =  0

    
    return response(json.dumps(logged))

def bareLogout(request):
    logout(request)
    return response(json.dumps(1))

def viewSessions(request):
    sessions = Session.objects.all()
    session = sessions[0]
    return render('presence/session_list.html', locals() )

def login_page(request):
    redirect_page = request.GET['next']
    
@login_required
def close_slashroot(request):
    '''
    Goodbye, and Goodnight. Lights Out.
    '''
    os.system('ssh -i /home/power/.ssh/id_rsa power@10.0.0.127 -o StrictHostKeyChecking=no "heyu alloff A"')
    slashroot=Location.objects.get(id=1)
    LocationState.objects.create(name='closed', color='red', creator=request.user, location=slashroot)
    return HttpResponse(1)

def open_slashroot(request):
    '''
    I don't know why you say Goodbye, I say Hello. Hello, Hello. Lights On.
    '''
    os.system('ssh -i /home/power/.ssh/id_rsa power@10.0.0.127 -o StrictHostKeyChecking=no "heyu allon A"')
    slashroot=Location.objects.get(id=1)
    LocationState.objects.create(name='closed', color='red', creator=request.user, location=slashroot)
    return HttpResponse(1)
        