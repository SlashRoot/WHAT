"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from unittest import expectedFailure
import json

from contact.forms import handle_user_profile_form
from django.http import HttpRequest
from contact.views import new_contact
from django.contrib.auth.models import User

class ContactInfoTests(TestCase):
    

    @expectedFailure
    def test_contact_profile_shows_contact_info(self):
        self.fail()
    
    @expectedFailure
    def test_contact_profile_shows_proper_phone_number(self):
        self.fail()

    def test_contact_info_form_submits_even_if_user_does_not_have_profile(self):
        user_who_has_no_profile = User.objects.create(username="no_profile_willie")
        user_who_has_no_profile.set_password('password')
        user_who_has_no_profile.save()
        
        reasonable_sample_post_string = '{"user_id": %s, "user-first_name": "Willie", "user-last_name": "Nopro", "user-email": "willie@noprofiles.com", "phone_new-type": "", "phone_new-number": "", "phone_get-number": "555-555-5225", "phone_get-type": "mobile", "csrfmiddlewaretoken": "9a672a2d2ef6c1a5592e3ba338b6012d"}' % user_who_has_no_profile.id
        reasonable_sample_post_dict = json.loads(reasonable_sample_post_string)
        
        self.client.login(username="no_profile_willie", password="password")
        response = self.client.post('/contact/new_contact/', reasonable_sample_post_dict, follow=True)

        self.assertEqual(response.status_code, 200) #Necessary but not sufficient.
        
        self.assertTrue(user_who_has_no_profile.userprofile) #After that has been run, they now need to have a profile.
        self.assertTrue(user_who_has_no_profile.userprofile.contact_info) #....and also a ContactInfo object.
        
        self.assertEqual(response.redirect_chain, [('http://testserver%s' % user_who_has_no_profile.userprofile.contact_info.get_absolute_url(), 302)]) #If all went well, we were redirected to the absolute url of the ContactInfo object that we just created.
        

class PageLoadTests(TestCase):

    def test_new_contact(self):
        pass