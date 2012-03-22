import random

from django import forms
from django.contrib.auth.models import User

from people.models import UserProfile

from contact.models import ContactInfo

from contact.models import PhoneNumber, PHONE_NUMBER_TYPES

from utility.widgets import SelectMonthAndDayWidget
from people.functions import get_profile_and_contact_for_user

class UserForm(forms.ModelForm):
    class Meta:
        model=User

class UserContactForm(forms.ModelForm):
    class Meta:
        model=User
        #exclude = ['date_joined', 'username', 'password', 'is_staff', 'is_active', 'is_superuser', 'last_login']
        fields = ('first_name', 'last_name', 'email' )

class UserContactInfoForm(forms.ModelForm):    
    class Meta:
        model = ContactInfo
        exclude = ['websites'] 

class PhoneNumberForm(forms.ModelForm):

    class Meta:
        model = PhoneNumber
        exclude = ("owner")

class UserProfileForm(forms.ModelForm):
    #Turn the phone field into a text widget instead of multiselect
    birthday = forms.CharField(max_length=8, widget = SelectMonthAndDayWidget(), required=False )
    
    class Meta:
        model=UserProfile
        fields = ('political_party',)
    
def handle_user_profile_form(user_form, contact_form, profile_form, phone_forms, user=False):
    '''
    Take user and profile forms and test and save them.
    If all goes well, we'll return False.
    If the forms are invalid, we'll return them.
    '''
    
    #Deal with phone forms
    if phone_forms:
        phone_forms_valid = True #If there are any phone forms, we'll consider them valid until we find otherwise.
        for phone_form in phone_forms:
            if not phone_form.is_valid():
                phone_forms_valid = False        
    else:
        phone_forms_valid = True #We'll consider them valid if there aren't any at all.
        
    
    
    if user_form.is_valid() and contact_form.is_valid() and profile_form.is_valid() and phone_forms_valid: #All portions of the form are in fact valid. 
        if user: #We are modifying an existing user.
            profile, contact = get_profile_and_contact_for_user(user) #TODO: This can sometimes return False, which breaks the logic below.
            user_form.instance = user
            
            #They may not yet have a UserProfile and / or ContactInfo object.  Let's find out and do some special logic.            
            if profile:
                profile_form.instance = profile
            else:
                profile = profile_form.instance = UserProfile.objects.create(user=user)
            
            if contact:
                contact_form.instance = contact
            else:
                contact = contact_form.instance = ContactInfo.objects.create()
                profile_form.instance.contact_info = contact_form.instance
                profile_form.instance.save()
            
        else:               
            #Use the User objects manager to generate a random password    
            random_password = User.objects.make_random_password()
            
            #Get the instances from each form.
            user    = user_form.instance
            user.is_active = False
            contact = contact_form.instance
            profile = profile_form.instance
            
            #Set this user's password to the random password we just generated
            user.set_password(random_password)
            
            #Set their username to their email address for now - unless it is blank!
            if not user_form.cleaned_data['email'] == '':
                user.username = user_form.cleaned_data['email']
            else:
                #Set the username to the first name plus a random integer.
                user.username = user_form.cleaned_data['first_name'] + str(random.randint(0, 999999))
        
        #Save this new user.
        user_form.save()
        
        #Relate the user to the profile
        profile.user = user
        
        #Save the profile for now.
        contact_form.save()
        
        profile.contact_info=contact
        
        #No intention of mucking with the profile, so we can save that.
        profile_form.save()
        
        for phone_form in phone_forms:
            phone_form.instance.save(owner=contact) #Use instead of the form's .save() method because we need to pass this kwarg in order to establish the M2M
            phone_number = phone_form.instance
        
            #Now that it has a pk, associate it with the M2M table for PhoneNumber....
            #contact.phone_numbers.add(phone_number) #Now performed by the kwarg in the save method above
        
        #...and save it again.
        contact.save()
        
        return False #Everything went OK, so we'll just return False to tell them that there were no errors.
        
    else:#One or more of the four forms has errors.
        forms = [user_form, contact_form, profile_form], phone_forms #Setup the forms variable so that we can send them back to the template to display error messages.
        
        return forms