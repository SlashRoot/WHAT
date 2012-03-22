"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

import json
from unittest.case import expectedFailure



class WhoAmITests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('fishmonkey')
        self.user.save()
        
    
    def test_username_is_properly_returned(self):
        
        self.client.login(username='testuser', password='fishmonkey')
        response = self.client.get('/api/whoami/')
        self.assertTrue(response, 200)
        
        content = response.content
        user_info_dict = json.loads(content)
        username = user_info_dict["username"]  #tests that users can log in and view a user restricted page
        self.assertEqual(username, "testuser")
        
        
class ProfileTests(TestCase):
    
    @expectedFailure    
    def test_profile_absolute_url_raises200(self):
        self.fail()
        
    @expectedFailure    
    def test_profile_contains_list_of_phone_numbers_and_urls(self):
        '''
        People's profiles need to contain the ability to contact them.
        '''
        self.fail()
    
    @expectedFailure    
    def test_avatar_upload(self):
        self.fail()
        
