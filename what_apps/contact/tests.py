from unittest import expectedFailure
import json

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.conf import settings

from what_apps.contact.forms import handle_user_profile_form
from what_apps.contact.management.commands.emailhandler import get_first_text_part, Command as EmailHandlerCommand
from what_apps.contact.views import new_contact
from what_apps.contact.models import MailHandler

from what_apps.people.models import UserProfile, Role, Group, RoleInGroup
from what_apps.do.tests import make_task_tree
from what_apps.do.models import Task
from what_apps.email_blast.models import BlastMessage


class IncomingEmailTests(TestCase):
    
    def test_email_to_user_is_parsed(self):
        user = User.objects.create(username="George")
        profile = UserProfile.objects.create(user=user, email_prefix="george")
    
#        sample_basic_raw_email_to_handler = open('%s/apps/contact/management/commands/sample_email_info.txt' % settings.PROJECT_ROOT, 'r')
    
    def test_email_to_handler_is_parsed(self):
        MailHandler.objects.create(address="test-handler") 
        email_handler_command = EmailHandlerCommand()
        
        email_msg = email_handler_command.handle('%s/what_apps/contact/management/commands/sample_email_to_handler.txt' % settings.PROJECT_ROOT )
        
        pass
    
    def test_email_to_object_is_parsed(self):
        ron = User.objects.create(username="rlumbergh", email="ron_lumbergh@innotrode.com") #Email matches "sender" in our test email doc
        ron.set_password('password')
        ron.save()
        
        make_task_tree(self) #So that we have a Task object to which to send this message.
        
        email_handler_command = EmailHandlerCommand()
        
        #This email text is from Ron Lumbergh, the user above.  The innotrode guy - the young guy.
        #It is to do.task.1@objects.slashrootcafe.com - the email address of the task we made using make_task_tree.
        email_msg = email_handler_command.handle('%s/what_apps/contact/management/commands/sample_email_to_object.txt' % settings.PROJECT_ROOT )

        task = Task.objects.get(id=1) #Here's the task to which we sent the email.
        #Now Ron will login and verify that his message is displayed on the page.
        
        self.client.login(username="rlumbergh", password="password")
        task_url_response = self.client.get(task.get_absolute_url())
        self.assertTrue("Llamas are awesome." in task_url_response.content)
        
    def test_email_to_blast(self):
        self.assertFalse(BlastMessage.objects.filter(message__contains="llamas").exists())
        
        role = Role.objects.create(name="scholar")
        group = Group.objects.create(name="Knights of the Round Table")
        role_in_group = RoleInGroup.objects.create(role=role, group=group)
        brother_maynard = User.objects.create(username="brother_maynard", email="bmaynard@armaments.camelot.co.uk")
        
        email_handler_command = EmailHandlerCommand()
        email_handler_command.handle('%s/what_apps/contact/management/commands/sample_email_to_blast.txt' % settings.PROJECT_ROOT )
        
        self.assertTrue(BlastMessage.objects.filter(message__contains="Llamas are awesome.").exists())

    def test_email_to_blast_from_unknown_user(self):
        email_handler_command = EmailHandlerCommand()
        email_msg = email_handler_command.handle('%s/what_apps/contact/management/commands/sample_email_blast_from_unknown_user.txt' % settings.PROJECT_ROOT )
        self.assertFalse(email_msg)

class ContactInfoTests(TestCase):
    

    @expectedFailure
    def test_contact_profile_shows_contact_info(self):
        self.fail()
    
    @expectedFailure
    def test_contact_profile_shows_proper_phone_number(self):
        self.fail()

    def test_contact_info_form_submits_even_if_user_does_not_have_profile(self):
        user_who_has_no_profile = User.objects.create(username="no_profile_willie")
        user_who_has_no_profile.set_password('password')
        user_who_has_no_profile.save()
        
        reasonable_sample_post_string = '{"user_id": %s, "user-first_name": "Willie", "user-last_name": "Nopro", "user-email": "willie@noprofiles.com", "phone_new-type": "", "phone_new-number": "", "phone_get-number": "555-555-5225", "phone_get-type": "mobile", "csrfmiddlewaretoken": "9a672a2d2ef6c1a5592e3ba338b6012d"}' % user_who_has_no_profile.id
        reasonable_sample_post_dict = json.loads(reasonable_sample_post_string)
        
        self.client.login(username="no_profile_willie", password="password")
        response = self.client.post('/contact/new_contact/', reasonable_sample_post_dict, follow=True)

        self.assertEqual(response.status_code, 200) #Necessary but not sufficient.
        
        self.assertTrue(user_who_has_no_profile.userprofile) #After that has been run, they now need to have a profile.
        self.assertTrue(user_who_has_no_profile.userprofile.contact_info) #....and also a ContactInfo object.
        
        self.assertEqual(response.redirect_chain, [('http://testserver%s' % user_who_has_no_profile.userprofile.contact_info.get_absolute_url(), 302)]) #If all went well, we were redirected to the absolute url of the ContactInfo object that we just created.
        

class PageLoadTests(TestCase):

    def test_new_contact(self):
        pass
    
class SpamSelectionTests(TestCase):
    
    @expectedFailure
    def spam_number_does_not_send_outgoing_calls(self):
        self.fail()
        
    def phone_number_profile_contains_spam_checkbox(self):
        self.fail()