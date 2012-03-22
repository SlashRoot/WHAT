from django.test import TestCase
from sandbox.models import Giraffe, Event, Attendee


#class GiraffeTest(TestCase):
#    
#    def test_that_giraffe_has_spots(self):
#        giraffe = Giraffe()
#        self.assertTrue(giraffe.has_spots(), "there's no spots man")

class AttendanceTest(TestCase):
    def test_that_attendees_are_counted(self):
        event = Event.objects.create()
        self.assertEqual(0, event.attendees.count())
        
        attendee = Attendee.objects.create(event=event)
        self.assertEqual(1, event.attendees.count())
        
#ServiceCheckin
#test that button on top of page exists
  #get page ('/service/the_situation')
  #see if my box is in the HTML generated there

#test that submitting form improperly raises error

#test that submitting form properly causes new Service to be created
#test that submitting form properly causes new Service to be listed in situation

        