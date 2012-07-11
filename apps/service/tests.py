from comm.tests import create_phone_calls
from contact.models import ContactInfo, PhoneNumber
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from do.config import set_up as do_setup, set_up_privileges
from do.models import Task
from mellon.config import set_up as mellon_setup
from people.models import UserProfile
from service.config import set_up as service_setup
from service.models import Service, ServiceStatusLog, ServiceStatusPrototype, ManualPriceAdjustment
from unittest import expectedFailure
from utility.models import FixedObject
import datetime
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
            
        return service


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
    def test_add_billable_hour_to_service_price_tag(self):
        self.fail()
        
    @expectedFailure
    def test_add_billable_hour_to_list_of_charges(self):
        self.fail()
        
    @expectedFailure
    def test_list_of_charges_creates_a_dict_listing_amounts_charged_and_for_what(self):
        self.Fail()
        
    @expectedFailure
    def test_pricetagprototype_is_specific_to_individual_customer(self):
        self.Fail()
    
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
        
    def test_status_duration_is_detected(self):
        service = self.test_service_profile_page_lists_statuses()
        status = ServiceStatusPrototype.objects.create(name="test_status", always_in_bearer_court=True)
        now = ServiceStatusLog.objects.create(prototype=status,
                                        service=service,
                                        creator=self.admin,
                                        )
        before = ServiceStatusLog.objects.create(prototype=status,
                                        service=service,
                                        creator=self.admin,
                                        )
        before.created -= datetime.timedelta(days=17, hours=12)
        before.duration()
        self.assertEqual(before.duration().days, 
                               17,
                               )
        return service, status
    
    def test_how_many_times_in_status(self):
        service, status = self.test_status_duration_is_detected()  # Status has already been set twice.
        instances = service.total_time_in_status(status)[0]
        self.assertEqual(instances, 2)
        
    def test_timedelta_of_total_duration(self):
        service = self.test_service_profile_page_lists_statuses()
        old_prototype = ServiceStatusPrototype.objects.create(name="On The Bench", always_in_bearer_court=True)
        new_prototype = ServiceStatusPrototype.objects.create(name="new_status", always_in_bearer_court=True)
        
        total_time_in_new_status = service.total_time_in_status("new_status")[1]
        self.assertFalse(total_time_in_new_status)  # We haven't spent any time in this status yet.
        
        old_status = ServiceStatusLog.objects.create(service=service, prototype=old_prototype, creator=self.admin)
        new_status = ServiceStatusLog.objects.create(service=service, prototype=new_prototype, creator=self.admin)
        
        
        old_status.created -= datetime.timedelta(days=11, hours=2) #So that the duration of the test doesn't screw it up
        old_status.save()
        
        total_time_in_old_status = service.total_time_in_status(old_status)[1]
        
        self.assertTrue(total_time_in_old_status > total_time_in_new_status)
        self.assertEqual(total_time_in_old_status.days, 11)
        
        old_status_redux = ServiceStatusLog.objects.create(service=service, prototype=old_prototype, creator=self.admin)
        new_status_redux = ServiceStatusLog.objects.create(service=service, prototype=new_prototype, creator=self.admin)
        
        old_status_redux.created -= datetime.timedelta(4)
        old_status_redux.save()
        
        number_of_times_in_old_status, total_time_in_old_status = service.total_time_in_status(old_status)
        
        self.assertEqual(number_of_times_in_old_status, 2)
        self.assertEqual(total_time_in_old_status.days, 15)
        
        return service
    
    def test_service_status_summary(self):
        service = self.test_timedelta_of_total_duration()
        summary = service.status_summary()
        self.assertEqual(summary[0][0], 'On The Bench')
        self.assertEqual(summary[1][0], 'new_status')
        
    def test_service_status_summary_on_template(self):
        
        service = self.test_timedelta_of_total_duration()
        response = self.client.get(service.get_absolute_url())
        self.assertTrue('15 days' in response.content) #TODO: This is not ideal - it just proves that the phrase appears, not that it appears near the appropriate status.  Make this a better test.

    def test_total_price_of_service(self):
        '''
        Takes the duration of time spent 'On the bench', multiplies by 
        pay_per_hour(rate we charge for service per hour) and either
        adds or subtracts from manual_override (should one exist).
        '''   
        
        service = self.test_timedelta_of_total_duration()  # service has already spent (some time) on the bench
        service.pay_per_hour = 70.00
        service.adjustments.create(amount=20.00, service=service, description="awesome person")
        
        total = service.total_price()
        
        self.assertEqual(total, 25360.0)


class AdjustmentFormTests(TestCase):
    def setUp(self):
        do_setup()
        service_setup()
        
        mellon_setup()
        set_up_privileges()
        
        people.config.set_up()
        
        self.admin = User.objects.create(is_superuser=True, username="admin", password="admin", first_name="Youhan")
        self.admin.set_password('admin')
        self.admin.save()
                    
    def test_rate_and_adjustment(self):

        self.client.login(username="admin", password="admin")
        check_in_response = self.client.post('/service/check_in/', {'customer':'auth.user_2___admin', 'projected':'12/21/2012'}, follow=True)
        service = Service.objects.all()[0]
        ticket_dict = {'pay_per_hour':70.00, 
                       'amount':20.00,
                       'description':'awesome!'}
        ticket_response = self.client.post(service.get_absolute_url(), ticket_dict)
        
        pay_per_hour = service.pay_per_hour
        self.assertEqual(pay_per_hour, 70.00)
    
        try:
            adjustment = service.adjustments.get(amount=20.00)
        except Service.DoesNotExist, Service.MultipleObjectsReturned:
            self.fail('%s adjustment objects were created.  Expecting 1.' % ManualPriceAdjustment.objects.count())

        #If we got this far, exactly one adjustment exists.  Good.
        
        