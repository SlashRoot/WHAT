"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from unittest import expectedFailure

class CustodyTests(TestCase):
    
    @expectedFailure
    def test_device_status_log(self):
        self.fail()
        
    @expectedFailure    
    def test_device_current_status(self):
        self.fail()
    
    @expectedFailure    
    def test_device_is_listed_by_status(self):
        self.fail()
        
    @expectedFailure    
    def test_device_plunder_causes_device_to_be_retired(self):
        '''
        That upon plundering a device, it is no longer in the ecosystem.
        '''
        self.fail()
        
    @expectedFailure    
    def test_device_plunder_causes_new_devices_to_be_created(self):
        self.fail()
    
    @expectedFailure    
    def test_device_location(self):
        self.fail()
        
    @expectedFailure    
    def test_all_comments_on_device(self):
        '''
        Gathers comments from do, service, people, presence, and wherever else may have relations to this device.
        '''
        self.fail()
        
    