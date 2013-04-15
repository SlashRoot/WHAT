from .forms import UserContactForm, UserContactInfoForm, UserProfileForm, \
    handle_user_profile_form, PhoneNumberForm
from .models import ContactInfo, Message, DialList, DialListParticipation, \
    PhoneNumber, BICYCLE_DAY
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.http import HttpResponseRedirect as redirect, HttpResponse, Http404
from django.shortcuts import render
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from what_apps.utility.forms import GenericPartyField, SimplePartyLookup
from what_apps.people.models import UserProfile
from what_apps.utility.functions import daily_crypt
import datetime


class ContactForm(ModelForm):
    class Meta:
        model = Message

def contact_form(request):
    form=ContactForm()
    
    return render(request, 'contact_form.html', locals())

@login_required
def contact_list(request):
    people = User.objects.all().order_by('last_name')
    return render(request, 'contact/contact_list.html', locals())


def contact_profile(request, contact_id=None, username=None):
    if contact_id:
        contact = ContactInfo.objects.get(id=contact_id)
    if username:
        contact = User.objects.get(first_name=username) #TODO: Turn into actual username, un-fuckify

    contact_info = contact.__dict__.items()

    return render(request, 'contact/contact_profile.html', locals())

@login_required
def new_contact(request):
    '''
    Adds or modifies a contact.
    Makes a User object (and a UserProfile and ContactInfo) for them.
    '''
    
    #We're going to have two lists of forms; one for the three objects, and one for phone numbers.
    contact_forms = []
    phone_forms = []
    blank_phone_form = PhoneNumberForm(prefix="phone_new")
    
    if request.POST: #Are we posting new information?
        
        #First let's figure out if we are dealing with an existing user or adding a new one.
        try:
            referenced_user = User.objects.get(id=request.POST['user_id'])
        except MultiValueDictKeyError:
            referenced_user = False #We didn't get a user passed in via POST.
    
        user_form = UserContactForm(request.POST, prefix="user")
        contact_form = UserContactInfoForm(request.POST, prefix="contact")
        profile_form = UserProfileForm(request.POST, prefix="profile")
        
        #Now we need to traverse the dict to pick out the phone forms.
        #They may come in three types:
        #phone_n, where n is the id of a PhoneNumber object - these are existing PhoneNumber objects
        #phone_new - these are phone number objects added with the "add phone" button
        #phone_get - this is the phone number passed into the form originally (used if you click "new contact" from a PhoneCall Task page.)
        populated_phone_forms = []
        for item, value in request.POST.items():
            #Take note: item will be something like phone_new-number-2
            if item.split('_')[0] == "phone": 
                #Look for phone items, but only branch off once per phone (ie, only on the "number," not the "type")                
                if item.split('_')[1].split('-')[1] == "number":
                    try:
                        entry = item.split('_')[1].split('-')[2] #Which entry is this?  There might be more than one number. 
                        type_string = str(item.split('-')[0]) + "-type-" + entry
                    except IndexError: #This is not a numbered entry.
                        type_string = str(item.split('-')[0]) + "-type"
                    type = request.POST[type_string] 
                    number = value
                    
                    if not(not number and not type): #We only want cases where both number and type are not blank.  If either is filled in, we'll proceed.
                    
                        case_indicator = item.split('_')[1].split('-')[0] #This will be either n, "new", or "get" as per above.
                        
                        if case_indicator == "new" or case_indicator == "get" or 0:
                            try:
                                phone_number_object = PhoneNumber.objects.get(number=number)
                                populated_phone_forms.append(PhoneNumberForm({'number':number, 'type':type}, instance=phone_number_object))
                            except PhoneNumber.DoesNotExist:
                                populated_phone_forms.append(PhoneNumberForm({'number':number, 'type':type}))
                                                    
                            
                        else: #Assume that it's the n case
                            phone_number_object = PhoneNumber.objects.get(id=case_indicator)
                            populated_phone_forms.append(PhoneNumberForm({'number':number, 'type':type}, instance=phone_number_object))
        
        
        #Send the forms to the handler for processing.
        invalid = handle_user_profile_form(user_form, contact_form, profile_form, populated_phone_forms, user = referenced_user) #Returns forms tuple if forms are invalid; False otherwise

        if not invalid: #Here we'll do something special if the handling went as we hoped.
            '''
            SUCCESS!
            '''
            if 'profile-birthday_month' in request.POST:
                profile_form.instance.birth_month = request.POST['profile-birthday_month']
                profile_form.instance.birth_day = request.POST['profile-birthday_day']
            profile_form.instance.save()
            
            #If wasn't working here.  strange.  TODO: Change from try block to if.  :-)
            try: #TODO: Justin and Kieran say: do this with sessions
                role = request.GET['role']
                if role == 'donor':
                    
                    #Not good here - I want direct access to the user object by now.  REFORM! (People like that reform, pappy)
                    encrypted_user_id = daily_crypt(user_form.instance.id) #Get the user id, encrypt it. 
                    
                    return redirect('/accounting/record_donation/?donor=' + encrypted_user_id)
                
            except LookupError: #Probably ought to be some different branching here - they don't ALWAYS need to go to watch calls.
                
                #Oh, and BTW, this is SUCCESS.
                return redirect(contact_form.instance.get_absolute_url()) #Send them to the contact page.
            
        
                    
        else: #Not valid - let's tell them so.
            contact_forms, phone_forms = invalid
            return render(request, 'contact/new_contact.html', locals())
        
        

    else: #No POST - this is a brand new form.
        contact_forms = [UserContactForm(prefix="user"), UserContactInfoForm(prefix="contact"), UserProfileForm(prefix="profile")]
    
        #We want email, first name, and last name to be required for all submissions.
        contact_forms[0].fields['email'].required = True
        contact_forms[0].fields['first_name'].required = True
        contact_forms[0].fields['last_name'].required = True
        
        
        try: #This might be a "new contact from phone number" request.  Let's find out.
            phone_forms.append(PhoneNumberForm(initial = {'number': request.GET['phone_number']}, prefix="phone_get")) #Yes it is! Put the phone number in the field.                  
        except MultiValueDictKeyError: 
            pass #No, it isn't.  Move along.  Nothing to see here.
    

    
    #Either we don't have POST (meaning this is a brand new form) or something is invalid.
    #In either case, let's set the fields to required and give them the template again.
    initial_lookup_form = SimplePartyLookup()
    
    return render(request, 'contact/new_contact.html', locals())

@login_required #TODO: More security
def contact_forms_for_person(request):
    contact_forms = []
    phone_forms = []
    
    referenced_user = User.objects.get(id=request.GET['user_id'])
    user_form = UserContactForm(prefix="user", instance=referenced_user)
    contact_forms.append(user_form)
    blank_phone_form = PhoneNumberForm(prefix="phone_new")
    
    try:
        userprofile = referenced_user.userprofile
        profile_form = UserProfileForm(prefix="profile", instance=userprofile)
        try:
            contact_info = userprofile.contact_info
            contact_form = UserContactInfoForm(prefix="contact", instance=contact_info)
            contact_forms.append(contact_form)
                        
            for phone_number in contact_info.phone_numbers.all():
                phone_forms.append(PhoneNumberForm(instance=phone_number, prefix="phone_%s" % (phone_number.id)))
                
            
        except ContactInfo.DoesNotExist:
            contact_form = UserContactInfoForm(prefix="contact")
            
        contact_forms.append(profile_form)
        
    except UserProfile.DoesNotExist:
        profile_form = UserProfileForm(request.POST, prefix="profile")
        
    try:
        phone_forms.append(PhoneNumberForm(initial = {'number': request.GET['phone_number']}, prefix="phone_get"))
    except MultiValueDictKeyError:
        pass
    
    return render(request, 'contact/new_contact_inside_form.html', locals())

def toggle_dial_list(request, dial_list_id):
    dial_list = DialList.objects.get(id=dial_list_id)
    phone_number_id = request.POST['data']
    phone_number_object = PhoneNumber.objects.get(id = phone_number_id)
    
    active = False if request.POST['truthiness'] == 'false' else True
    
    if active:
        DialListParticipation.objects.create(
                                           number = phone_number_object,
                                           list = dial_list,
                                           )
    else:
        try:
            latest = DialListParticipation.objects.get(number = phone_number_object, list=dial_list, destroyed = BICYCLE_DAY)
            latest.destroyed = datetime.datetime.now()
            latest.save()
        except DialListParticipation.DoesNotExist:
            #Ummmm, they weren't on the list in the first place.  No need to take them off it.
            pass
        
    return HttpResponse(1)

def phone_number_profile(request, phone_number_id):
    phone_number = PhoneNumber.objects.get(id=phone_number_id)
    
    if request.POST:
        phone_number.spam = int(request.POST['spam'])
        phone_number.save()
    
    return render(request, 'contact/phone_number_profile.html', locals())