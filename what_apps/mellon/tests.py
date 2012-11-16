"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from unittest.case import expectedFailure

class RankTests(TestCase):
    @expectedFailure    
    def test_proper_rank_can_load_restricted_page(self):        
        self.fail()
        
    @expectedFailure    
    def test_lack_of_proper_rank_cannot_load_restricted_page(self):
        self.fail()

    @expectedFailure    
    def test_privilege_in_one_organization_grants_access_for_resources_in_that_organization(self):
        self.fail()
    
    @expectedFailure    
    def test_priviliege_in_some_organization_does_not_grant_access_in_other_organization(self):
        self.fail()
        
    @expectedFailure    
    def test_automatic_badge_award(self):
        '''
        That some conditions automatically grant the awarding of a badge.
        '''
        self.fail()
        
    @expectedFailure    
    def test_manual_badge_award(self):
        self.fail()
        
    @expectedFailure    
    def test_score_is_properly_calculated(self):
        self.fail()

    @expectedFailure    
    def test_new_card_is_saved(self):
        self.fail()
    
    @expectedFailure    
    def test_card_swipe(self):
        self.fail()
        
    @expectedFailure    
    def test_card_that_is_not_associated_a_user_does_nothing(self):
        self.fail()
        
    @expectedFailure    
    def test_card_that_is_associated_with_a_user_provides_session(self):
        self.fail()
        
    @expectedFailure    
    def test_bunk_card_gives_proper_error(self):
        self.fail()
        
    @expectedFailure    
    def test_temporary_card_is_created(self):
        self.fail()
        
    @expectedFailure    
    def test_temporary_card_expires_on_time(self):
        self.fail()
        
    @expectedFailure    
    def test_user_logged_in_via_card_can_access_logged_in_only_pages(self):
        self.fail()
        
    @expectedFailure    
    def test_user_logged_in_via_card_cannot_access_pages_that_are_password_only(self):
        self.fail()
    
    @expectedFailure    
    def test_that_card_authentication_may_only_come_from_authorized_physical_machines(self):
        '''
        We don't want people to be able to spoof a hash and login via hacked ajax over the wifi.
        Thus, we need to ensure that only authorized computers may allow card swipage.
        '''
        self.fail()
    
    