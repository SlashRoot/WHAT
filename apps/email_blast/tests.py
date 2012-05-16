from django.core import mail
from django.test import TestCase
from unittest import expectedFailure

from email_blast.models import BlastMessage
from people.models import Group, Role, RoleInGroup, UserInGroup
from django.contrib.auth.models import User

class BlastFormTest(TestCase):
    def test_if_blast_form_is_200(self):
        response = self.client.get('/blast_form/')
        self.assertEqual(response.status_code, 200)
        
    def test_if_blast_form_gathers_data(self):
        form = self.client.post('/blast_form/', {'subject':'Testing', 'message':'One, Two', 'role':'King', 'group':'Castle', 'send_to_higher_role':True})
        self.assertEqual(form.status_code, 200)
    
    
    def test_that_blast_email_populates_a_list_of_email_addresses(self):
        al = User.objects.create(username="Al", email="example@example.com")
        ted = User.objects.create(username="Ted", email="dot@something.com")
        sue = User.objects.create(username="Sue", email="pancakelover@bettysue.net")
        
        larpers = Group.objects.create(name="Larper")
        
        mage = Role.objects.create(name="Mage")
        archer = Role.objects.create(name="Archer")
        knight = Role.objects.create(name="Knight")
        
        mage_in_larper = RoleInGroup.objects.create(role=mage, group=larpers)
        archer_in_larper = RoleInGroup.objects.create(role=archer, group=larpers)
        knight_in_larper = RoleInGroup.objects.create(role=knight, group=larpers)
        
        al_the_knight = UserInGroup.objects.create(user=al, role=knight_in_larper)
        ted_the_knight = UserInGroup.objects.create(user=ted, role=knight_in_larper)
        sue_the_mage = UserInGroup.objects.create(user=sue, role=mage_in_larper)
        
        blast_message = BlastMessage.objects.create(subject='Attention Larpers!', message="You must save the queen from the sorceress Ann O'Rexia", role=knight, group=larpers, send_to_higher_roles=False)
        
        target_emails = blast_message.populate_targets()
    
        self.assertTrue(al.email in target_emails)
        self.assertTrue(ted.email in target_emails)
        self.assertFalse(sue.email in target_emails)
        
        
        
        
        
    @expectedFailure    
    def test_if_email_is_sent(self):
        self.fail()
        

    