from django.test import TestCase
from service.models import Service

from contact.models import PhoneNumber, ContactInfo
from people.models import UserProfile, UserInGroup
from django.contrib.auth.models import User

from do.config import set_up_privileges

import do.config
import service.config as service_config
import mellon.config
import people.config
from comm.tests import create_phone_calls
from utility.models import FixedObject


class ResolveCallsModels(TestCase):
    def setUp(self):
        do.config.set_up()
        service_config.set_up()
        
        mellon.config.set_up()
        set_up_privileges()
        
        people.config.set_up()
        
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
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_client.id in exclusive_response.content)
        
    def test_member_is_listed_among_members(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {'member_to':True, 
                                                            'member_from':True,                                                            
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_member.id in inclusive_response.content)
        
    def test_member_is_not_listed_among_non_members(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'client_to':True, 
                                                            'unknown_caller_from':True,                                                            
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_member.id in inclusive_response.content)
        
    def test_other_known_caller_is_listed_among_other_known_callers(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', { 
                                                            'other_known_caller_from':True,                                                            
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_other_known.id in inclusive_response.content)
        
    def test_other_known_caller_aint_listed_among_non_other_known_callers(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'client_to':True,
                                                            'member_from':True,                                                            
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_other_known.id in inclusive_response.content)
    
    def test_unknown_caller_is_listed_among_unknown_callers(self):
        inclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'unknown_caller_from':True,
                                                            'client_to':True,                                                        
                                                            'submitted_filter_form':True
                                                            })
        self.assertTrue('resolve_%s' % self.call_from_unknown.id in inclusive_response.content)
    
    def test_unknown_caller_aint_listed_among_non_unknown_callers(self):
        exclusive_response = self.client.get('/comm/resolve_calls/', {
                                                            'client_to':True,
                                                            'member_from':True,                                                            
                                                            'submitted_filter_form':True
                                                            })
        self.assertFalse('resolve_%s' % self.call_from_unknown.id in exclusive_response.content)
        
    

