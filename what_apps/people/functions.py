from what_apps.contact.models import ContactInfo
from .models import UserProfile


def get_profile_and_contact_for_user(user):
    '''
    Takes a user and returns a tuple of profile and contact_info for that user, returning False for either if they don't exist.
    '''
    try:
        #First let's see if they have a user profile.
        userprofile = user.userprofile
        try:
            contact_info = userprofile.contact_info
        except ContactInfo.DoesNotExist:
            contact_info = False
        
    except UserProfile.DoesNotExist:
        #Well shit.  They don't have a userprofile, so they also don't have a contact info object; at least not one that we know about.
        userprofile = False
        contact_info = False
    
    return userprofile, contact_info