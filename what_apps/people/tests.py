"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from what_apps.people.models import Group, Role, RoleInGroup, RoleHierarchy

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


class RoleStructureTests(TestCase):
    def test_role_returns_upward_hierarchy(self):
        group = Group.objects.create(name="some_group")
        
        low_role = Role.objects.create(name='lowest_role')
        medium_role = Role.objects.create(name="medium_role")
        high_role = Role.objects.create(name="highest_role")
        
        RoleHierarchy.objects.create(lower_role=low_role, higher_role=medium_role, jurisdiction=group)
        RoleHierarchy.objects.create(lower_role=medium_role, higher_role=high_role, jurisdiction=group)
        
        higher_roles = low_role.get_higher_roles(group)
        
        expected_role_list = [medium_role, high_role]
        self.assertTrue(higher_roles == expected_role_list)

        
class RoleFormTests(TestCase):
    def test_that_form_posts_data_and_redirects_to_confirmation_page(self):
        admin = User.objects.create(username="admin")
        admin.set_password('seamonkey')
        admin.save()
        
        self.client.login(username="admin", password="seamonkey")
        
        user = User.objects.create(username="Jacob")
        role = Role.objects.create(name="Sweeper")
        group = Group.objects.create(name="Reptile Monkey Massage INC.")
        
        response = self.client.post('/people/role_form/', {'user':'auth.user_%s__Jacob' % user.id, 'role':role.id, 'group':group.id})
    
        self.assertEqual(response.status_code, 302)
        
        redirect_response = self.client.get('/people/awesome/')
        self.assertEqual(redirect_response.status_code, 200)
        
        monkey_massage_sweepers = RoleInGroup.objects.get(role=role, group=group)
        self.assertTrue(user in monkey_massage_sweepers.users().all())
        
        
        
        