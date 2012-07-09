from fluidbarter.models import TradeItem, TradeElement, PaymentMethod,\
    QuantificationUnit, QuantificationDimension, ExchangeInvolvement, RealThing
from django.test import TestCase
from unittest import expectedFailure
from utility.tests.factories import UserFactory, GroupFactory
from django.contrib.auth.models import Group
from fluidbarter.tests.factories import TradeElementFactory

import people.config
from fluidbarter.tests.test_functions import response_from_purchase_form,\
    get_main_and_item_forms, get_buyer_and_seller
from fluidbarter.exchange_functions import get_purchase_details, exchange_between_parties, buy_item


class PurchaseFunctionTests(TestCase):
    def setUp(self):
        people.config.set_up()
        get_buyer_and_seller(self)
        
        self.pay_meth = PaymentMethod.objects.create(name="test_payment_method")
        testdim = QuantificationDimension.objects.create(name="test_dimension")
        self.qu = QuantificationUnit.objects.create(name="test_unit", abbreviation="tu", dimension=testdim)
        self.quantity = 5
        self.te = TradeElementFactory.create(name="test_element")
        
    def test_create_exchange(self):
        exchange = exchange_between_parties([self.buyer, self.seller], self.buyer_user)
        self.assertTrue(exchange)

    def test_involvements_are_properly_returned(self):
        exchange, involvements = exchange_between_parties([self.buyer, self.seller], self.buyer_user, return_involvements=True)
        self.assertEqual(exchange.parties.get(party=self.buyer), involvements[self.buyer])
        self.assertEqual(exchange.parties.get(party=self.seller), involvements[self.seller])

    def test_buy_item(self):
        exchange, involvements = exchange_between_parties([self.buyer, self.seller], self.buyer_user, return_involvements=True)
        seller_pledge, buyer_pledge = buy_item(
                     seller_involvement = involvements[self.seller],
                     buyer_involvement = involvements[self.buyer],
                     trade_element = RealThing,
                     trade_element_kwargs = {'element': self.te, 'unit of quantification':self.qu, 'amount':4},
                     price=60,
                     payment_method=self.pay_meth,
                     quantity = self.quantity,   
                     deliver = True,
                     group = True,
                     )

        self.assertTrue(seller_pledge.group())
        self.assertTrue(buyer_pledge.group())

class PurchaseFormTests(TestCase):
    def setUp(self):
        people.config.set_up()
        get_buyer_and_seller(self)
        
        self.pay_meth = PaymentMethod.objects.create(name="test_payment_method")
        testdim = QuantificationDimension.objects.create(name="test_dimension")
        self.qu = QuantificationUnit.objects.create(name="test_unit", abbreviation="tu", dimension=testdim)
        self.quantity = 5
        self.te = TradeElementFactory.create(name="test_element")
        
        # A POST dict consistent with our form.  TODO: Figure out a way to actually extract this from the view logic or the form.
        self.purchase_form_dict = {
                      'other_party': [u'people.group_%s___%s' % (self.seller.id, self.seller.name)],
                      u'Other_Item-TOTAL_FORMS': [u'1'],
                      u'Other_Item-MAX_NUM_FORMS': [u''],
                      u'Device-INITIAL_FORMS': [u'0'],
                      u'Other_Item-0-deliver': [u'on'],
                      u'Device-TOTAL_FORMS': [u'0'],
                      u'Ingredient-INITIAL_FORMS': [u'0'],
                      u'payment_method': self.pay_meth.id,
                      u'Ingredient-TOTAL_FORMS': [u'0'],
                      u'purchase_date': [u'06/23/2012'],
                      u'csrfmiddlewaretoken': [u'VzeQ8IC0Hv9jeNikXjqqLeHaGGiYbqzl'],
                      u'receipt_image': [u''],
                      u'Other_Item-INITIAL_FORMS': [u'0'],
                      u'Ingredient-MAX_NUM_FORMS': [u''],
                      u'-0-undefined': [u'Lamp Module'],
                      u'Other_Item-0-group': [u'on'],
                      u'Device-MAX_NUM_FORMS': [u''],
                      u'Other_Item-0-unit of quantification': self.qu.id,
                      u'Other_Item-0-price_per': [u'2.00'],
                      u'Other_Item-0-quantity': self.quantity,
                      u'Other_Item-0-amount': [u'2'],
                      u'Other_Item-0-element': [u'fluidbarter.tradeelement_%s___%s' % (self.te.id, self.te.name)]
                      } 
    '''
    client tests
    '''
    
    def test_record_purchase_submit_redirects_to_seller_involvement(self):                
        response = response_from_purchase_form(self)
        self.assertEqual(response.status_code, 200)

        seller_involvement = ExchangeInvolvement.objects.get(party__group=self.seller)

        redirected_to = response.redirect_chain[0][0]
        proper_url = seller_involvement.get_absolute_url()
        url_is_proper = redirected_to.endswith(proper_url)

        self.assertTrue(url_is_proper)

    def test_seller_involvement_is_grouped_for_group_checked_on_form(self):
        response = response_from_purchase_form(self)
        seller_involvement = ExchangeInvolvement.objects.get(party__group=self.seller)

        group = seller_involvement.get_pledge_clusters().values()[0][1][0].group()
        
        self.assertTrue(group)
        self.assertEqual(group['display'], self.te.name)
        self.assertEqual(group['quantity'], self.quantity)
    
    def test_seller_involvement_is_not_grouped_for_group_unchecked_on_form(self):
        self.purchase_form_dict['Other_Item-0-group'] = ''
        
        response = response_from_purchase_form(self)
        seller_involvement = ExchangeInvolvement.objects.get(party__group=self.seller)
        
        group = seller_involvement.get_pledge_clusters().values()[0][1][0].group()
        self.assertFalse(group)

class FoundationsOfCommerce(TestCase):
    def setUp(self):
        self.trade_element = TradeElement.objects.create(name="oven mit", description="great for preventing burns.")
        self.tradeitem = RealThing.objects.create(element=self.trade_element)

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
    
    

    