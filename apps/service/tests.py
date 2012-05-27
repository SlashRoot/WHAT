from django.test import TestCase

from django.contrib.auth.models import User

from unittest import expectedFailure
from service.models import Service, ServiceStatusLog, ServiceStatusPrototype

from do.config import set_up as do_setup
from do.config import set_up_privileges
from service.config import set_up as service_setup
from mellon.config import set_up as mellon_setup
from do.models import Task
from utility.models import FixedObject
from django.http import HttpResponse
from comm.tests import create_phone_calls
from people.models import UserProfile
from contact.models import ContactInfo, PhoneNumber
import people.config

class CurrentClients(TestCase):
    def setUp(self):
        do_setup()
        service_setup()
        
        mellon_setup()
        set_up_privileges()
        
        people.config.set_up()
        
        self.admin = User.objects.create(is_superuser=True, username="admin", password="admin", first_name="Youhan")
        self.admin.set_password('admin')
        self.admin.save()
        
    def tearDown(self):
        ServiceStatusLog.objects.all().delete()
        Task.objects.all().delete()
        
    def test_service_client_is_listed_among_clients_on_resolve_calls_page_only_with_client_checked (self):
        self.client.login(username="admin", password="admin")    
        service = self.test_service_check_in_form_creates_service_object()
        UserProfile.objects.create(user=service.recipient.user, contact_info=ContactInfo.objects.create())       
        jingle = PhoneNumber.objects.create(owner=service.recipient.user.userprofile.contact_info, number="+18456797779")
        calls = create_phone_calls(1,from_number=jingle)

        response = self.client.get('/comm/resolve_calls/', {'client':True})
        self.assertTrue('resolve_%s' % calls[0].id in response.content)

        response = self.client.get('/comm/resolve_calls/', {'client':False})
        self.assertFalse('resolve_%s' % calls[0].id in response.content)

    def test_service_check_in_form_creates_proper_task(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post('/service/check_in/', {'customer':'auth.user_2___admin', 'projected':'12/21/2012'}, follow=True)
        task = Task.objects.all()[0]
        tp = FixedObject.objects.get(name="TaskPrototype__tech_service").object
        self.assertTrue(task.prototype, tp)

    def test_service_check_in_form_creates_service_object(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post('/service/check_in/', {'customer':'auth.user_2___admin', 'projected':'12/21/2012'}, follow=True)
        service = Service.objects.all()[0]
        self.assertTrue(service.recipient.user, self.admin)
        
        return service
    
    def test_service_ticket_raises_404_if_does_not_exist(self):
        self.client.login(username="admin", password="admin")
        service_id = 1234567
        try:
            service = Service.objects.get(id=service_id)
            self.fail('the object wasnt supposed to exist but it does')
        except Service.DoesNotExist:
            response = self.client.get('/service/tickets/%s/' % service_id)
            self.assertEqual(response.status_code, 404)
        
    def test_service_in_our_court_at_first(self):
        service = self.test_service_check_in_form_creates_service_object()
        self.assertTrue(service in Service.objects.filter_by_needing_attention()[0])
        
    def test_service_profile_page__(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post('/service/check_in/', {'customer':'auth.user_2___admin', 'projected':'12/21/2012'}, follow=True)
        service = Service.objects.all()[0]
        
        profile_response = self.client.get(service.get_absolute_url())
        self.assertEqual(profile_response.status_code, 200)
        
    def test_service_profile_page_lists_statuses(self):
        self.client.login(username="admin", password="admin")
        response = self.client.post('/service/check_in/', {'customer':'auth.user_2___admin', 'projected':'12/21/2012'}, follow=True)
        service = Service.objects.all()[0]
        
        profile_response = self.client.get(service.get_absolute_url())
        for status in ServiceStatusPrototype.objects.filter(retired__isnull=True):
            self.assertTrue(status.name in profile_response.content)


    def test_service_archive_not_logged_redirect_to_login(self):
        self.client.logout()
        response = self.client.get('/service/archive/', follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], 'http://testserver/presence/login/?next=/service/archive/')
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_service_archive_logged_in_200(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get('/service/archive/')
        self.assertEqual(response.status_code, 200)
        
        
    def test_completed_service_appears_on_service_archive_but_not_situation(self):
        service = self.test_service_check_in_form_creates_service_object()
        service.task.set_status(creator=self.admin, status=2)
        
        archive_response = self.client.get('/service/archive/')
        situation_response = self.client.get('/service/the_situation')
        
        self.assertTrue(service.recipient.user.first_name in archive_response.content)
        self.assertFalse(service.recipient.user.first_name in situation_response.content) 
        
    

    @expectedFailure
    def test_uncompleted_service_tasks_are_listed_in_situation(self):
        self.fail()
            
    @expectedFailure
    def test_number_of_days_is_calculated(self):
        self.fail()
        
    @expectedFailure
    def test_all_incoming_calls_from_service_recipient(self):
        self.fail()
        
    @expectedFailure
    def test_send_email_from_service_ticket(self):
        self.fail()
        
    @expectedFailure
    def test_post_client_visible_message(self):
        self.fail()
        self.all()[0].status.always_in_bearer_courtself.all()[0].staself.all()[0].status.always_in_bearer_courttus.always_in_bearer_court
    
    @expectedFailure
    def test_change_message_visibility(self):
        self.fail()

    @expectedFailure
    def test_service_contract_pdf_is_generated(self):
        self.fail()

    @expectedFailure
    def test_service_invoice_pdf_is_generated(self):
        self.fail()

    @expectedFailure
    def test_service_report_pdf_is_generated(self):
        self.fail()
        
    @expectedFailure
    def test_must_be_ranked_to_see_situation(self):
        self.fail()
    
    @expectedFailure    
    def test_add_billable_hour_to_service(self):
        self.fail()
    
    def test_status_ball_in_bearer_court_needs_attention(self):
        '''
        That a service job with a status for which the ball is in the court of the bearer shows as needing attention.
        '''
        service = self.test_service_check_in_form_creates_service_object()
        status = ServiceStatusPrototype.objects.create(name="test_status", always_in_bearer_court=True)
        
        self.assertTrue(service in Service.objects.filter_by_needing_attention()[0])

    @expectedFailure        
    def test_most_recent_call_unresolved_needs_attention(self):
        service = self.test_service_check_in_form_creates_service_object()
        self.fail()
    