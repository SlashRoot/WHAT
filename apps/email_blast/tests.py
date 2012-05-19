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
        
    def test_if_blast_form_prepares_data(self):
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
        
        blast_message = BlastMessage.objects.create(subject='Attention Larpers!', message="You must save the queen from the sorceress Ann O'Rexia", role=knight, group=larpers, creator=ted)
        
        target_emails = blast_message.populate_targets()
    
        self.assertTrue(al.email in target_emails)
        self.assertTrue(ted.email in target_emails)
        self.assertFalse(sue.email in target_emails)
        
           
    def test_if_email_is_sent(self):
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
        
    