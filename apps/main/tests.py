"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class Something(TestCase):
    
    def test_see_if_the_page_raises_200(self):
        
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200, 'Sorry, something does not exist, please try again.')
        
        

    def test_confirm_element_is_there(self):
        
        pass