from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from jinja2.ext import do
from what_apps.comm.tests import create_phone_calls
from what_apps.contact.models import PhoneNumber, ContactInfo
from what_apps.do.config import set_up_privileges, set_up as do_set_up
from what_apps.mellon.config import set_up as mellon_set_up
from what_apps.people.models import UserProfile, UserInGroup
from what_apps.service.models import Service
from what_apps.slashroot.config import set_up as slashroot_set_up
from what_apps.utility.models import FixedObject
import what_apps.service.config as service_config




class NavigationTests(TestCase):
    
    def setUp(self):
        cache.clear()
        slashroot_set_up()
        self.rusty = User.objects.create(is_superuser=True, username="rusty", first_name="Rusty", last_name="Spike")
        UserProfile.objects.create(user=self.rusty, contact_info=ContactInfo.objects.create())
        member_role = FixedObject.objects.get(name="RoleInGroup__slashroot_holder").object
        UserInGroup.objects.create(role=member_role, user=self.rusty)
                
        self.rusty.set_password('password')
        self.rusty.save()
        
        self.client.login(username="rusty", password="password")
    
    def test_no_unresolved_calls_are_listed_in_navigation_bar(self):
        response = self.client.get('/')
        self.assertTrue("Resolve Calls (0)" in response.content)
        
    def test_some_unresolved_calls_are_listed_in_nav_bar(self):
        calls = create_phone_calls(17, from_user=self.rusty)
        response = self.client.get('/')
        self.assertTrue("Resolve Calls (17)" in response.content)

        return calls

    def test_resolved_calls_are_not_counted_in_nav_bar(self):
        calls = self.test_some_unresolved_calls_are_listed_in_nav_bar()
        calls_to_resolve = calls[0:3] #Grab three of the calls....
        
        #And loop through them, resolving each.
        for call in calls_to_resolve:
            call.set_resolve_status(2, self.rusty)
        
        response = self.client.get('/')
        
        #This will be 14 because there were 17 calls originally.
        self.assertTrue("Resolve Calls (14)" in response.content)

class ResolveCallsModels(TestCase):
    def setUp(self):
        do_set_up()
        service_config.set_up()
        
        mellon_set_up()
        set_up_privileges()
        
        slashroot_set_up()
        
        #Create a known number for people to call.
        operator = User.objects.create(username="operator", first_name="Operator")
        UserProfile.objects.create(user=operator, contact_info=ContactInfo.objects.create())
        self.known_number = PhoneNumber.objects.create(owner=operator.userprofile.contact_info, number="+11231231234")
        
        
        #Create a member and login.
        rusty = User.objects.create(is_superuser=True, username="rusty", first_name="Rusty", last_name="Spike")
        UserProfile.objects.create(user=rusty, contact_info=ContactInfo.objects.create())
        member_role = FixedObject.objects.get(name="RoleInGroup__slashroot_holder").object
        UserInGroup.objects.create(role=member_role, user=rusty)
                
        rusty.set_password('password')
        rusty.save()
        
        self.client.login(username="rusty", password="password")
         
        PhoneNumber.objects.create(owner=rusty.userprofile.contact_info, number="+18456797712")
        self.call_from_member = create_phone_calls(1, from_user=rusty, to_number=self.known_number)[0]
        
        #Create a service / tech client.        
        martha = User.objects.create(username="martha", first_name="Martha")
        martha.set_password('password')
        martha.save()
        
        response = self.client.post('/service/check_in/', {'customer':'auth.user_%s___%s' % (martha.id, martha.username), 'projected':'12/21/2012'}, follow=True)
        service = Service.objects.all()[0]        
        UserProfile.objects.create(user=service.recipient.user, contact_info=ContactInfo.objects.create())       
        PhoneNumber.objects.create(owner=service.recipient.user.userprofile.contact_info, number="+18456797779")
        self.call_from_client = create_phone_calls(1, from_user=service.recipient.user, to_number=self.known_number)[0]
        
        
        #Create an "other known caller."
        somebody_else = User.objects.create(username="somebody_else", first_name="somebody")
        UserProfile.objects.create(user=somebody_else, contact_info=ContactInfo.objects.create())
        PhoneNumber.objects.create(owner=somebody_else.userprofile.contact_info, number="+18456797723")
        self.call_from_other_known = create_phone_calls(1, from_user=somebody_else, to_number=self.known_number)[0]
        
        
        #Create an unknown caller.
        unknown_number = PhoneNumber.objects.create(number="+18456797756")
        self.call_from_unknown = create_phone_calls(1, from_number=unknown_number, to_number=self.known_number)[0]
    
    def test_all_calls_are_listed_by_default(self):
        inclusive_response = self.client.get('/comm/resolve_calls/')
        self.assertTrue('resolve_%s' % self.call_from_client.id in inclusive_response.content)
        self.assertTrue('resolve_%s' % self.call_from_member.id in inclusive_response.content)
        self.assertTrue('resolve_%s' % self.call_from_other_known.id in inclusive_response.content)
        self.assertTrue('resolve_%s' % self.call_from_unknown.id in inclusive_response.content)

    def test_client_is_listed_among_clients(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {'client_to':True, 
                                                            'client_from':True,         
                                                            'include_without_recordings':True,                                                   
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_client.id in inclusive_response.content)

    def test_client_is_not_listed_among_non_clients(self):
        exclusive_response = self.client.get('/comm/resolve_calls/', {'client_to':False, 
                                                            'client_from':False,
                                                            'member_to':True, 
                                                            'member_from':True,
                                                            'other_known_caller_from':True,
                                                            'unknown_caller_to':True, 
                                                            'unknown_caller_from':True,
                                                            'include_without_recordings':True,
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_client.id in exclusive_response.content)
        
    def test_member_is_listed_among_members(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {'member_to':True, 
                                                            'member_from':True,
                                                            'include_without_recordings':True,                                               
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_member.id in inclusive_response.content)
        
    def test_member_is_not_listed_among_non_members(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'client_to':True, 
                                                            'unknown_caller_from':True,
                                                            'include_without_recordings':True,                                                            
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_member.id in inclusive_response.content)
        
    def test_other_known_caller_is_listed_among_other_known_callers(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', { 
                                                            'other_known_caller_from':True,
                                                            'include_without_recordings':True,                                                         
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_other_known.id in inclusive_response.content)
        
    def test_other_known_caller_aint_listed_among_non_other_known_callers(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'client_to':True,
                                                            'member_from':True,
                                                            'include_without_recordings':True,                                             
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_other_known.id in inclusive_response.content)
    
    def test_unknown_caller_is_listed_among_unknown_callers(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'unknown_caller_from':True,
                                                            'include_without_recordings':True,
                                                            'client_to':True,                                                        
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_unknown.id in inclusive_response.content)
    
    def test_unknown_caller_aint_listed_among_non_unknown_callers(self):
        exclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'client_to':True,
                                                            'member_from':True,
                                                            'include_without_recordings':True,                                             
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_unknown.id in exclusive_response.content)
        
    

