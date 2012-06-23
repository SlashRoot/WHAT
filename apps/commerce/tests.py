from django.test import TestCase
from commerce.models import TradeItem, TradeElement

from mechanize import Browser
from unittest import expectedFailure

class BasicCommerceViewsTests(TestCase):
    def test_record_purchase_page_200(self):
        response = self.client.get('/commerce/record_purchase/')
        self.assertEqual(response.status_code, 200, "The record purchase page did not return a 200.")
    
    
    def test_record_purchase_submit(self):
        purchase_form_dict = {
                              'other_party':1,
                              'payment_method':1,
                              'purchase_date':10/10/2010,
                              }
        response = self.client.post('/commerce/record_purchase/', purchase_form_dict)
        self.fail()
    
    def test_record_bill_page(self):
        response = self.client.get('/commerce/record_bill/')
        self.assertEqual(response.status_code, 200)


class FoundationsOfCommerce(TestCase):
    def setUp(self):
        self.trade_element = TradeElement.objects.create(name="oven mit", description="great for preventing burns.")
        self.tradeitem = TradeItem.objects.create(description="")

    @expectedFailure
    def test_trade_modeling(self):
        self.fail()


class SeriousFuckingNumbers(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    @expectedFailure
    def test_overall_assets_entity1(self):
        self.fail()
    
    @expectedFailure
    def test_overall_assets_entity2(self):
        self.fail()
    
    @expectedFailure
    def test_total_income_today(self):
        self.fail()
        
    @expectedFailure
    def test_total_expenses_today(self):
        self.fail()
    
    @expectedFailure
    def test_total_income_this_moon(self):
        self.fail()
    
    @expectedFailure
    def test_total_expenses_this_moon(self):
        self.fail()
    
    @expectedFailure
    def test_total_moneybags_all_time(self):
        self.fail()
    


class TraditionalBarter(TestCase):
    
    @expectedFailure
    def trade_item_for_item(self):
        self.fail()
    
    

    