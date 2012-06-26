from commerce.models import TradeItem, TradeElement, PaymentMethod,\
    QuantificationUnit, QuantificationDimension
from django.test import TestCase
from unittest import expectedFailure
from utility.tests.factories import UserFactory, GroupFactory
from django.contrib.auth.models import Group
from commerce.tests.factories import TradeElementFactory

import people.config

class BasicCommerceViewsTests(TestCase):
    def setUp(self):
        people.config.set_up()

        self.member = UserFactory.create(password="password")

    def test_record_purchase_page_200(self):
        response = self.client.get('/commerce/record_purchase/')
        self.assertEqual(response.status_code, 200, "The record purchase page did not return a 200.")
    
    def test_record_purchase_submit(self):
        group = GroupFactory.create(name="test_group")
        te = TradeElementFactory.create(name="test_element")
        paymeth = PaymentMethod.objects.create(name="test_payment_method")
        testdim = QuantificationDimension.objects.create(name="test_dimension")
        qu = QuantificationUnit.objects.create(name="test_unit", abbreviation="tu", dimension=testdim)

        self.client.login(username=self.member.username, password="password")
        purchase_form_dict = {
                              'other_party': [u'people.group_%s___%s' % (group.id, group.name)],
                              u'Other_Item-TOTAL_FORMS': [u'1'],
                              u'Other_Item-MAX_NUM_FORMS': [u''],
                              u'Device-INITIAL_FORMS': [u'0'],
                              u'Other_Item-0-deliver': [u'on'],
                              u'Device-TOTAL_FORMS': [u'0'],
                              u'Ingredient-INITIAL_FORMS': [u'0'],
                              u'payment_method': paymeth.id,
                              u'Ingredient-TOTAL_FORMS': [u'0'],
                              u'purchase_date': [u'06/23/2012'],
                              u'csrfmiddlewaretoken': [u'VzeQ8IC0Hv9jeNikXjqqLeHaGGiYbqzl'],
                              u'receipt_image': [u''],
                              u'Other_Item-INITIAL_FORMS': [u'0'],
                              u'Ingredient-MAX_NUM_FORMS': [u''],
                              u'-0-undefined': [u'Lamp Module'],
                              u'Other_Item-0-group': [u'on'],
                              u'Device-MAX_NUM_FORMS': [u''],
                              u'Other_Item-0-unit of quantification': qu.id,
                              u'Other_Item-0-price_per': [u'2.00'],
                              u'Other_Item-0-quantity': [u'14'],
                              u'Other_Item-0-amount': [u'2'],
                              u'Other_Item-0-element': [u'commerce.tradeelement_%s___%s' % (te.id, te.name)]
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
    
    

    