from django.core import mail
from django.test import TestCase
from unittest import expectedFailure

from email_blast.models import BlastMessage

class BlastFormTest(TestCase):
    def test_if_blast_form_is_200(self):
        response = self.client.get('/blast_form/')
        self.assertEqual(response.status_code, 200)
        
    def test_if_blast_form_gathers_data(self):
        form = self.client.post('/blast_form/', {'subject':'Testing', 'message':'One, Two', 'role':'King', 'group':'Castle', 'send_to_higher_role':True})
        self.assertEqual(form.status_code, 200)
    
    @expectedFailure    
    def test_if_email_is_sent(self):
        self.fail()
        

    