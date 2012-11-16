from django.test import TestCase
from pos.models import TemporarySaleModel

class SimplePosLoadingTests(TestCase):
    
    def test_that_pos_page_200(self):
        response = self.client.get('/pos/')
        self.assertEqual(response.status_code, 200)
        
class ActualSales(TestCase):
    '''
    this is just to integrate the features of the spreadsheet into a working form temporarily until made better.
    '''
    good_post_dict = {
                     'item':'latte',
                     'price':3.92,
                     'size':'medium',
                     'milk':'whole',
                     'taxable': True,
                     }
    def test_sale_POST(self):
        response = self.client.post('/pos/sales/', self.good_post_dict, follow=True)
        self.assertEqual(response.status_code, 200)
        
        
    def test_sale_is_saved(self):
        TemporarySaleModel.objects.all().delete()
        response = self.client.post('/pos/sales/', self.good_post_dict, follow=True)
        #self.assertEqual(TemporarySaleModel.objects.count(),1)
        
        