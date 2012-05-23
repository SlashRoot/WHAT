from unittest import expectedFailure

from django.test import TestCase
from django.contrib.auth.models import User

from do.tests import make_task_tree
from social.models import DrawAttention, TopLevelMessage
from people.models import GenericParty, Group, UserInGroup, Role, RoleInGroup
import do.config
from utility.tests import test_user_generic_party_factory

class MessageTests(TestCase):
    
    @expectedFailure
    def test_that_messages_are_restructred_text(self):
        self.fail()

class AttentionTests(TestCase):
    def setUp(self):
        #Remember, the GenericPartyManager's .get() method is more of a get-or-create flow
        self.sender = User.objects.create(username="sender")
        self.target_user = GenericParty.objects.get(party = User.objects.create(username="target_user"))
        
    def test_draw_attention_object_to_user_is_created(self):
        DrawAttention.objects.create(creator=self.sender, target=self.target_user, content_object=self.sender) #I'm drawing your attention to me! Look at me look at me! Mom! Mom! Mom! Maaa! Maaa! Maaaaa! Maaaa! (WHAT?!) Hi.
    
    def test_draw_attention_object_to_user_is_somewhat_acknowledged(self):
        d = DrawAttention.objects.create(creator=self.sender, target=self.target_user, content_object=self.sender)
        self.assertFalse(d.is_somewhat_acknowledged())
        
        d.acknowledge(user = self.target_user.user)
        self.assertTrue(d.is_somewhat_acknowledged())
        
    def test_acknowledge_draw_attention_via_ajax(self):
        d = DrawAttention.objects.create(creator=self.sender, target=self.target_user, content_object=self.sender)
        self.assertFalse(d.is_somewhat_acknowledged())
        response = self.client.post('/social/acknowledge/%s/' % d.id)
        self.assertTrue(d.is_somewhat_acknowledged())
       
       

def setUp_users_for_messages(test_case):    
    #Remember, the GenericPartyManager's .get() method is more of a get-or-create flow
    test_case.sender = User.objects.create(username="sender")
    test_case.sender.set_password('password')
    test_case.sender.save()
    test_case.target_user = GenericParty.objects.get(party = User.objects.create(username="target_user"))
    return test_case
       
class UserMessageTest(TestCase):
        
    good_post_dict_for_user_log = {'message':'I cleaned the bar'}
    good_post_dict_for_group_log = {'message':'hey all did we clean the bar tonight?'}
    
    def setUp(self):
        setUp_users_for_messages(self)
        do.config.set_up()
        
    def tearDown(self):
        TopLevelMessage.objects.all().delete()
        

    def test_top_level_message_is_log_returns_true_for_content_type_genericparty(self):
        message = TopLevelMessage.objects.create(creator=self.sender, content_object=self.target_user, message="i am a gremlin i am leaving the party and i want everyone to stuff the ice chest")
        is_log = message.is_log() 
        self.assertTrue(is_log)
    
    def test_top_level_message_is_log_returns_false_for_content_type_not_genericparty(self):
        make_task_tree(self) #A function we borrowed from the .do app.  Add .task_tree (a Task object) to this class.
        message = TopLevelMessage.objects.create(creator=self.sender, content_object=self.task_tree, message="Ding Dong Llama Wani Jumpin' With An Icepick She Thinks I'm...... Goin' in.")
        self.assertFalse(message.is_log())   

    def test_read_log_for_non_logged_in_user_redirects_to_login(self):
        response = self.client.get('/social/log/user/billy/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        redirected_to_login = response.redirect_chain[0] == ('http://testserver/presence/login/?next=/social/log/user/billy/', 302)
        self.assertTrue(redirected_to_login)    

    def test_read_somebody_elses_log_raises_403(self):
        self.client.login(username="sender", password="password")
        response = self.client.get('/social/log/user/billy/')
        self.assertEqual(response.status_code, 403)
    
    def test_read_log_for_user_returns_200(self):
        self.client.login(username="sender", password="password")
        response = self.client.get('/social/log/user/sender/')
        self.assertEqual(response.status_code, 200)
       
    def test_post_log_returns_200(self):
        response = self.client.post('/social/log/user/joe/', self.good_post_dict_for_user_log, follow=True)
        self.assertEqual(response.status_code, 200)
        
    def test_post_log_creates_new_log_for_user(self):
        sender_party = GenericParty.objects.get(party = self.sender)
        self.assertEqual(sender_party.messages.all().count(), 0)
        self.client.login(username="sender", password="password")
        post_response = self.client.post('/social/log/user/sender/', self.good_post_dict_for_user_log, follow=True)
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(sender_party.messages.all().count(), 1)
        
        result_response = self.client.get('/social/log/user/sender/')
        self.assertTrue(self.good_post_dict_for_user_log['message'] in result_response.content, msg='the new posted log is not in the log')
        
        
    
    
        

class GroupLog(TestCase):
    
    good_post_dict_for_user_log = {'message':'I cleaned the bar'}

    good_post_dict_for_group_log = {'message':'hey all did we clean the bar tonight?'}
    
    
    def setUp(self):
        self.users = setUp_users_for_messages(self)
                
        self.group = Group.objects.create(name='test_group')
        self.group_party = GenericParty.objects.get(party=self.group)     
        
        do.config.set_up()
        
    def tearDown(self):
        TopLevelMessage.objects.all().delete()

    def test_read_log_for_user_not_in_group_returns_403(self):
        group = Group.objects.create(name='billysbobs')
#        role = Role.objects.create(name="Dingo Keeper")
#        role_in_group = RoleInGroup.objects.create(role=role, group=group)
#        UserInGroup.objects.create(role=role_in_group, user=self.sender)
        
        self.client.login(username="sender", password="password")
        response = self.client.get('/social/log/group/billysbobs/')
        
        self.assertEqual(response.status_code, 403)
        
    def test_read_log_for_user_non_existant_group_returns_404(self):
        self.client.login(username="sender", password="password")
        response = self.client.get('/social/log/group/this_group_definitely_does_not_exist/')
        self.assertEqual(response.status_code, 404)


    def test_post_log_403_for_user_not_in_group(self):
        self.client.login(username="sender", password="password")
        response = self.client.post('/social/log/group/test_group/', self.good_post_dict_for_group_log, follow=True)
        self.assertEqual(response.status_code, 403)
        
    def test_post_log_for_user_in_group_creates_new_group_log(self):
        member = Role.objects.create(name="member")
        UserInGroup.objects.create(user=self.sender, role=RoleInGroup.objects.create(role=member, group=self.group))
        self.client.login(username="sender", password="password")
        response = self.client.post('/social/log/group/test_group/', self.good_post_dict_for_group_log, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.group_party.messages.all().count(), 1)       
        
        result_response = self.client.get('/social/log/group/test_group/')
        self.assertTrue(self.good_post_dict_for_group_log['message'] in result_response.content, msg='the new posted log is not in the log')
 
    def test_complete_personal_and_group_log_for_generic_party(self):
        '''
        test that users personal log and log for every group that they are in are properly returned for generic party
        '''
        sender_party = GenericParty.objects.get(party = self.sender)
        sender_log = TopLevelMessage.objects.complete_log(sender_party)
        self.assertEqual(sender_log.count(), 0)
        
        self.test_post_log_for_user_in_group_creates_new_group_log() #this will have made a message from the function above
        sender_log = TopLevelMessage.objects.complete_log(sender_party)
        
        self.assertEqual(sender_log.count(), 1)
        
        self.client.login(username="sender", password="password")
        post_response = self.client.post('/social/log/user/sender/', self.good_post_dict_for_user_log, follow=True)
        self.assertEqual(sender_log.count(), 2)
        
        dashboard_response = self.client.get('/iam/')
        
        for message in TopLevelMessage.objects.all():
            self.assertTrue(message.message in dashboard_response.content)
       

        
        
        
        
        
        
        
        
        
        
        
        
        
