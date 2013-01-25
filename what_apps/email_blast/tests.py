from .models import BlastMessage
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from unittest import expectedFailure
from what_apps.people.models import Group, Role, RoleInGroup, UserInGroup, \
    RoleHierarchy


class BlastFormTest(TestCase):
    def test_if_blast_form_is_200(self):
        admin = User.objects.create(username="admin")
        admin.set_password('seamonkey')
        admin.save()
        
        self.client.login(username="admin", password="seamonkey")
        response = self.client.get('/blast_form/')
        self.assertEqual(response.status_code, 200)
        
    def test_if_blast_form_prepares_data(self):
        admin = User.objects.create(username="admin")
        admin.set_password('seamonkey')
        admin.save()
        
        self.client.login(username="admin", password="seamonkey")
        form = self.client.post('/blast_form/', {'subject':'Testing', 'message':'One, Two', 'role':'King', 'group':'Castle', 'send_to_higher_role':True})
        self.assertEqual(form.status_code, 200)
    
class ContactInfoPopulationTests(TestCase):
    def setUp(self):
        self.users = {}
        self.groups = {}
        self.roles = {}
        
        self.users['al'] = User.objects.create(username="Al", email="example@example.com")
        self.users['ted'] = User.objects.create(username="Ted", email="dot@something.com")
        self.users['sue'] = User.objects.create(username="Sue", email="pancakelover@bettysue.net")
        
        self.groups['larpers'] = Group.objects.create(name="Larper")
        
        self.roles['mage'] = Role.objects.create(name="Mage")
        self.roles['archer'] = Role.objects.create(name="Archer")
        self.roles['knight'] = Role.objects.create(name="Knight")
        
        mage_in_larper = RoleInGroup.objects.create(role=self.roles['mage'], group=self.groups['larpers'])
        archer_in_larper = RoleInGroup.objects.create(role=self.roles['archer'], group=self.groups['larpers'])
        knight_in_larper = RoleInGroup.objects.create(role=self.roles['knight'], group=self.groups['larpers'])
        
        al_the_knight = UserInGroup.objects.create(user=self.users['al'], role=knight_in_larper)
        ted_the_knight = UserInGroup.objects.create(user=self.users['ted'], role=knight_in_larper)
        sue_the_mage = UserInGroup.objects.create(user=self.users['sue'], role=mage_in_larper)


    def test_blast_email_populates_a_list_of_email_addresses(self):    
        blast_message = BlastMessage.objects.create(
                                subject='Attention Larpers!', 
                                message="You must save the queen from the sorceress Ann O'Rexia", 
                                role=self.roles['knight'], 
                                group=self.groups['larpers'], 
                                creator=self.users['ted']
                                )
        target_emails = blast_message.populate_targets()
    
        self.assertTrue(self.users['al'].email in target_emails)
        self.assertTrue(self.users['ted'].email in target_emails)
        self.assertFalse(self.users['sue'].email in target_emails)
        
    def test_hierarchical_roles_properly_populated(self):
        RoleHierarchy.objects.create(lower_role=self.roles['knight'], 
                                     higher_role=self.roles['mage'],
                                     jurisdiction=self.groups['larpers']
                                     )
        
        blast_message = BlastMessage.objects.create(
                                subject='Attention Larpers!', 
                                message="You must save the queen from the sorceress Ann O'Rexia", 
                                role=self.roles['knight'], 
                                group=self.groups['larpers'], 
                                creator=self.users['ted'],
                                send_to_higher_roles=True
                                )
        target_emails = blast_message.populate_targets()
        self.assertTrue(self.users['sue'].email in target_emails)
           
    def test_email_is_sent(self):
        '''
        Ah, do you remember the scene from Office Space where the Bobs are going over Peter Gibbon's file?
        '''
        bill = User.objects.create(username="Bill", email="glacierformdomino@hotmail.com")
        bob1 = User.objects.create(username="Bob1", email="dpiaquadio@gmail.com")
        bob2 = User.objects.create(username="Bob2", email="darkcatholic619@aol.com")
        
        initech = Group.objects.create(name="IniTech")
        consultant = Role.objects.create(name="Consultant")
        
        consultant_at_initech = RoleInGroup.objects.create(role=consultant, group=initech)
        
        bob1_consultant_at_initech = UserInGroup.objects.create(user=bob1, role=consultant_at_initech)
        bob2_consultant_at_initech = UserInGroup.objects.create(user=bob2, role=consultant_at_initech)
        
        
        blast_message = BlastMessage.objects.create(subject="I'm gonna have to go ahead and disagree with you on that", message="Peter's been real flaky lately...", role=consultant, group=initech, creator=bill)
        
        preparation = blast_message.prepare()
        
        message_sent = blast_message.send_blast()
        
        self.assertEqual(message_sent,1)
        self.assertEqual(blast_message.subject, preparation[0])
        self.assertEqual(blast_message.message, preparation[1])
        self.assertEqual(blast_message.creator.email, preparation[2])
        self.assertEqual(blast_message.populate_targets(), preparation[3])
        
    def test_blast_confirmation_is_200(self):
        response = self.client.get('/blast_form/confirmation/')
        self.assertEqual(response.status_code, 200)