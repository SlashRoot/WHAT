from django.test import TestCase
from django.contrib.auth.models import User
from what_apps.people.models import GenericParty
from django.test.simple import DjangoTestSuiteRunner

from django.conf import settings

class WHATTestRunner(DjangoTestSuiteRunner):
    def run_tests(self, extra_tests=None, **kwargs):
        if not extra_tests:
            test_labels = settings.LOCAL_APPS #By default, we want to run only local tests.
        else:
            test_labels = extra_tests
        super(WHATTestRunner, self).run_tests(test_labels, extra_tests=None, **kwargs)

class WHATTestCase(TestCase):
    
    def assertStatusCode(self, url, hopeful_status_code):
        response = self.client.get(url)
        self.assertEqual(response.status_code, hopeful_status_code)
        return response
        
    def assertPageLoadSuccess(self, url):
        return self.assertStatusCode(url, 200)
    
    def assertLoginRequired(self, url):
        self.client.logout()
        response = self.client.get(url, follow=True)
        
        try:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.redirect_chain[0][0], 'http://testserver/presence/login/?next=%s' % url)
            self.assertEqual(response.redirect_chain[0][1], 302)
        except IndexError:
            self.fail('The redirect did not occur for %s' % url)
        
    def test_success_urls(self):
        try:
            for url in self.success_urls:
                self.assertPageLoadSuccess(url)
        except AttributeError:
            return True
            
    def test_login_required_urls(self):
        try:
            for url in self.login_required_urls:
                self.assertLoginRequired(url)
        except AttributeError:
            return True

def test_user_factory(number_of_users_to_create):
    '''
    pseudo factory. 
    takes an integer.
    returns a list of users.
    
    Obviously, don't use this to make production users.  Dominick.
    '''
    users = []
    
    while len(users) < number_of_users_to_create:
        user = User.objects.create(username='test_user_%s' % len(users))
        user.set_password('password')
        user.save()
        users.append(user)
        
    return users

def test_user_generic_party_factory(number_of_parties_to_create):
    user_list = test_user_factory(number_of_parties_to_create)
    party_list = []
    
    for user in user_list:
        party_list.append(GenericParty.objects.get(party=user))
    
    return party_list
    

    