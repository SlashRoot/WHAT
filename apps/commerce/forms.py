from django import forms
from django.forms.formsets import formset_factory

from django.contrib.auth.models import User

from commerce.models import RealThing, ExchangeInvolvement, MoneyBag, MoneyBagPiece, Exchange, PaymentMethod, TradeElement, QuantificationUnit


from hwtrack.models import Device, DeviceModel
from people.models import CommerceGroup, Member
from products.models import Beverage, IngredientStock, Ingredient, ProductBrand, IngredientProperty
from accounting.models import BudgetLine
from utility.forms import AutoCompleteField, MustBeUniqueField, RequiredFormSet, GenericPartyField, JqueryDatePicker
from utility.models import GenericPartyForeignKey


class DonationForm(forms.Form):
    other_party = AutoCompleteField(label="Donor", models=(User, CommerceGroup))
    
class SimpleMoneyForm(forms.Form):
    amount = forms.DecimalField(max_digits=16, decimal_places=2)
    method = forms.ModelChoiceField(queryset=PaymentMethod.objects.all())
    
class DonationRealThingForm(forms.Form):    
    real_thing_donation = AutoCompleteField(models=(RealThing,))    


class MainPOSForm(forms.Form): 
    '''
    for information that needs to be repeated multiple times in the sale. 
    for
     example, the member that records the sale.
    '''
    member = AutoCompleteField(models=(Member,))
    other_party = AutoCompleteField(label="Client", models=(User,))
    payment_method = forms.ModelChoiceField( queryset=PaymentMethod.objects.all() )
    '''
    client will be the link to the hardware track system so that we can be up to date on the clients' machine
    '''

class SaleForm(forms.Form):
    
    price = forms.DecimalField(max_digits=16, decimal_places=2)
#   taxable = forms.BooleanField() 

    
class BeverageSaleForm(SaleForm):
    '''
    record information for the beverage sale that will change with each sale.
    '''
    
    barista = AutoCompleteField(models=(Member,))    
    beverage = AutoCompleteField(models=(Beverage,))

class ComputerRentalForm(SaleForm):
    '''
    when a customer uses one of our computers
    '''
    
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
   
        
class ConsultationSaleForm(SaleForm):
    '''
    tech, web development, radical feminism, spackling, etc. consultation
    '''
    
    consultant = AutoCompleteField(models=(Member,))
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
      
    
class ComputerRepairSaleForm(SaleForm):
    '''
    for checking out tech bench customers for hardware or software repair
    '''
    product_name = 'Computer Repair'

class FoodSaleForm(SaleForm):
    '''
    selling of the yummy treats
    '''
    pass
        
        
class WebDevelopmentSaleForm(SaleForm):
    '''
    for checking out web dev clients
    '''
    pass


class PurchaseForm(forms.Form):
    '''
    This is a 'parent' form - not in the object sense, but in the logical sense:
    This form is filled out only once per purchase, while the item forms below are filled out once per item.
    '''
    other_party = GenericPartyField()
    payment_method = forms.ModelChoiceField(queryset=PaymentMethod.objects.all())
    receipt_image = forms.ImageField(required=False)
    purchase_date = JqueryDatePicker()

class BillForm(PurchaseForm):
    '''
    A purchase form for a RealThing for which we are being billed.
    '''
    billing_period_start = JqueryDatePicker()
    billing_period_end = JqueryDatePicker()
    due_date = JqueryDatePicker()

def purchase_form_factory(class_name, base, field_dict):
    always_has = {
                  'price_per': forms.DecimalField(widget=forms.TextInput(attrs={'class':'pricePer', 'size':'10'})),
                  'quantity': forms.IntegerField(widget=forms.TextInput(attrs={'class':'quantity', 'size':'4'})),
                  'group':forms.BooleanField(required=False),
                  'deliver':forms.BooleanField(required=False),                                    
                  }
    
    always_has.update(field_dict)
    return type(class_name,(base,), always_has)

def purchase_meta_factory(form_model, exclude_fields=None, include_fields=None):
    class Meta:
        model = form_model
        exclude = exclude_fields
        fields = include_fields
    return Meta

    
PurchaseItemForm = purchase_form_factory('PurchaseItemForm', forms.Form, {
    'unit of quantification': forms.ModelChoiceField(queryset=QuantificationUnit.objects.all() ),
    'amount':forms.IntegerField(widget=forms.TextInput(attrs={'size':'4'})),
    'item_name': AutoCompleteField(models=(TradeElement,), new_buttons=True),
    'description': forms.CharField(widget=forms.Textarea),
    })
    
PurchaseIngredientForm = purchase_form_factory('PurchaseIngredientForm', forms.Form, {
   'unit of quantification': forms.ModelChoiceField(queryset=QuantificationUnit.objects.all() ),
   'amount':forms.IntegerField(widget=forms.TextInput(attrs={'size':'10'})), 
   'brand': AutoCompleteField(models=(ProductBrand,), new_buttons=True),
   'ingredient': AutoCompleteField(models=(Ingredient,), new_buttons=True),
   'property':AutoCompleteField(required=False, models=(IngredientProperty,), new_buttons=True),
   })
            
PurchaseDeviceForm = purchase_form_factory('PurchaseDeviceForm', forms.Form, {
   'model': AutoCompleteField(models=(DeviceModel,), new_buttons=True),
   'Meta': purchase_meta_factory(Device, include_fields=['model'] ),
   })



#Ummmm, yep.  These be them.
THINGS_WE_PURCHASE = {
                      'Ingredient': [IngredientStock, PurchaseIngredientForm], 
                      'Device': [Device, PurchaseDeviceForm],
                      'Other_Item': [TradeElement, PurchaseItemForm],                          
                      }



    
def exchange_from_POST(post, member, transaction_type):
    '''
    NOW OUT OF DATE.
    
    Take a post object and parse it into a transaction.
    '''
    
    
    '''
    Harvest information about the transaction.
    '''
    
    purchase_post = post.copy()
    
    other_party_encrypted_info = purchase_post.pop('lookup_other_party')[0]
    
    other_party = party_from_encrypted_string(other_party_encrypted_info)
    
    #and these get the method with which money is exchanged
    method_id = purchase_post.pop('payment_method')[0]
    method = PaymentMethod.objects.get(id = method_id)


    '''
    And make the wheels spin.
    '''     
    money_bag = MoneyBag.objects.create(method = method) #A moneybag for the pieces to point to...
    cluster = Exchange.objects.create() #A cluster for the exchanges to point to...
    
    for key, value in purchase_post.items():#tuples, word, definition. word, definition. word, etc. 
        if key.split('_')[0] == 'item':#(items have the word "item" at the beginning of their key - is this one of those?)
            purchase_number = key.split('_')[1]#grabbing a purchase number from the key name
            price = purchase_post.pop('price_') + purchase_number#use the purchase number to look up price in dictionary
            description = purchase_post.pop('description_') + purchase_number#use the purchase number to get description
            budget_line_id = purchase_post.pop('budget_') + purchase_number
            budget_line = BudgetLine.objects.get(id = budget_line_id)
            
            #breaks spending of money_bag into pieces for ease of cataloging
            money_bag_piece = MoneyBagPiece.objects.create(money_bag = money_bag,
                                                           amount = price,
                                                           )
         
            item = RealThing.objects.create(name = value, 
                                            description = description, 
                                            )
           
            exchange = Exchange.objects.create(budget_line = budget_line,
                                              cluster = cluster,
                                              manager = member,
                                              )
         
               
            #This is the other party's contract for this exchange.
            contract = ExchangeInvolvement.objects.create(party = other_party,
                                               item = item,
                                               exchange = exchange,
                                               )
            contract.deliver()
            
            #And this is SlashRoot's contact for this exchange.
            contract = ExchangeInvolvement(
                                item = money_bag_piece,
                                exchange = exchange,
                                )
            contract.slashroot_as_party()
            contract.save()            
            contract.deliver()
            
        return exchange
        