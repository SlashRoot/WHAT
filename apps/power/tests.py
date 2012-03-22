"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from unittest.case import expectedFailure

class BasicPowerTests(TestCase):
    
    @expectedFailure    
    def test_new_power_device_creation(self):
        self.fail()
        

    @expectedFailure    
    def test_dim_a_light(self):
        self.fail()
        
    @expectedFailure    
    def test_turn_off_and_on_a_light(self):
        self.fail()
    
    