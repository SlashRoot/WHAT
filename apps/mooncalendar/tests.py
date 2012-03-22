"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import datetime

from django.test import TestCase
from mooncalendar.models import Moon
from unittest import expectedFailure


class MoonDatesTests(TestCase):
    
    def setUp(self):    
        self.before_moon = Moon.objects.create(
                                        name = "Before Moon",
                                        new = datetime.datetime(1776, 5, 17, 17, 14),
                                        waxing = datetime.datetime(1776, 5, 25, 8, 38),
                                        full = datetime.datetime(1776, 6, 2, 5, 37),
                                        waning = datetime.datetime(1776, 6, 9, 4, 24),
                                        )
        
        self.independence_moon = Moon.objects.create(
                                        name = "Independence Moon",
                                        new = datetime.datetime(1776, 6, 12, 3, 22),
                                        waxing = datetime.datetime(1776, 6, 24, 2, 10),
                                        full = datetime.datetime(1776, 7, 1, 15, 31),
                                        waning = datetime.datetime(1776, 7, 8, 8, 56),
                                        )
        self.after_moon = Moon.objects.create(
                                        name = "After Moon",
                                        new = datetime.datetime(1776, 7, 17, 3, 22),
                                        waxing = datetime.datetime(1776, 7, 26, 2, 10),
                                        full = datetime.datetime(1776, 8, 4, 15, 31),
                                        waning = datetime.datetime(1776, 8, 13, 8, 56),
                                        )
    def tearDown(self):
        Moon.objects.all().delete()
    
    def test_before_moon(self):
        '''
        that you can get the moon thats before the one your looking at
        '''
        
        previous_moon_as_determined_by_model_method = self.independence_moon.previous_moon()
        self.assertEqual(previous_moon_as_determined_by_model_method, self.before_moon) 
        
        
    def test_subsequent_moon(self):
        
        '''
        that you are looking one that comes after
        '''

        subsequent_moon_as_determined_by_model_method = self.independence_moon.subsequent_moon()
        self.assertEqual(subsequent_moon_as_determined_by_model_method, self.after_moon) 
    
            
    def test_that_date_is_before_moon(self):
       test_date =  datetime.datetime(1776, 6, 11, 3, 22) #Assigns a dummy date
       is_within, before_or_after = self.independence_moon.date_falls_within(test_date) #Pass the date to the ??? method so that we can get the result tuple
       self.assertFalse(is_within)#assert that the first element is False
       self.assertEqual(before_or_after, 'before')#assert that the second element is "Before"
    
    def test_that_date_is_within_moon(self):
       test_date = datetime.datetime(1776, 7, 5, 5, 11)
       is_within = self.independence_moon.date_falls_within(test_date)[0]
       self.assertTrue(is_within)
        
    def test_that_date_is_after_moon(self):
       test_date = datetime.datetime(1984, 8, 5, 3, 16)
       is_within, before_or_after = self.independence_moon.date_falls_within(test_date)
       self.assertFalse(is_within)
       self.assertEqual('after', before_or_after)
       
    def test_moon_absolute_url_page_loads_200(self):
        url = self.independence_moon.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    @expectedFailure
    def test_moon_dates_plausibility(self):
        self.fail()

    @expectedFailure        
    def test_create_new_event(self):
        self.fail()
    
    @expectedFailure
    def test_events_are_display_in_proper_moon(self):
        self.fail()
    
    @expectedFailure    
    def test_moons_appear_in_year(self):
        self.fail()
        
    @expectedFailure    
    def test_event_is_passed(self):
        self.fail()
        
    @expectedFailure    
    def test_users_birthday(self):
        self.fail()
        
    @expectedFailure    
    def test_automatic_event_creation(self):
        '''
        Some events occur at the same time during each moon.
        For example, we have migration day 10 days after each syzygy.
        '''
        self.fail()
        
    @expectedFailure    
    def test_automatic_event_retirement(self):
        self.fail()
    
    @expectedFailure    
    def test_automatic_event_display(self):
        self.fail()
    
    @expectedFailure    
    def test_event_report(self):
        '''
        We'll want to report on the happenings at events.
        This needs to work whether the event is manually created, automatically created, or implied by another app.
        '''
        self.fail()