from .exchange_functions import get_purchase_details, donation_from_POST
from .forms import ComputerRentalForm, PurchaseForm, MainPOSForm, \
    BeverageSaleForm, BillForm
from .models import ExchangeInvolvement, Exchange, Pledge
from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.utils.datastructures import MultiValueDictKeyError
from forms import DonationForm, SimpleMoneyForm, DonationRealThingForm, \
    THINGS_WE_PURCHASE, PurchaseIngredientForm
from what_apps.commerce.forms import exchange_from_POST
from what_apps.contact.forms import UserContactForm, UserContactInfoForm, \
    UserProfileForm
from what_apps.people.models import GenericParty
from what_apps.products.models import BeverageInstance



def record_purchase(request, is_bill=False):

    if is_bill:
        proper_form = BillForm
    else:
        proper_form = PurchaseForm
    
    main_form = proper_form()
    item_forms = []
    
    for prefix, [model, form_name] in THINGS_WE_PURCHASE.items():
        PurchaseSubFormSet = formset_factory(form_name, extra=0)
        if request.POST:
            item_formset = PurchaseSubFormSet(request.POST, prefix=prefix) 
        else: 
            item_formset = PurchaseSubFormSet(prefix=prefix)
        item_forms.append((item_formset, model)) #Pass a tuple each time.
            
    if request.POST:
        main_form = proper_form(request.POST, request.FILES)
        
        try:
            receipt_image = request.FILES['receipt_image'] 
        except MultiValueDictKeyError:
            receipt_image = None
            
        try:
            purchase_date = request.FILES['purchase_date'] 
        except MultiValueDictKeyError:
            purchase_date = None
    
        valid, details = get_purchase_details(
                                              main_form, 
                                              item_forms, 
                                              request.user.member, 
                                              receipt_image = receipt_image,
                                              date = purchase_date,
                                              )
    
        if not valid: #valid will be false if the forms were bunk.
            main_form = details[0]
            item_forms = details[1]
            show_errors = True
            return render(request, 'commerce/record_transaction.html', locals())
        else:
            return HttpResponseRedirect('/commerce/view_purchase/' + str(details[0].id))
    
      
    return render(request, 'commerce/record_transaction.html', locals())

def record_ingredient_order(request):
    '''
    Reflect an existing order for ingredients
    '''
    main_form = PurchaseForm(request.POST, request.FILES) if request.POST else PurchaseForm()
    
    item_forms = []
    prefix = 'ingredient'
    form_name = PurchaseIngredientForm
    PurchaseSubFormSet = formset_factory(form_name, extra=0)
    item_formset = PurchaseSubFormSet(request.POST, prefix=prefix) if request.POST else PurchaseSubFormSet(prefix=prefix)
    item_forms.append(item_formset)
    
    if request.POST:
        pass
    
    return render(request, 'commerce/record_transaction.html', locals())


def pos_modal(request):
    '''
    Display the POS modal
    TODO: Move submission handler somewhere else, make handler action dynamic
    '''
    if request.POST: #Is there incoming information?
        exchange_from_POST(request.POST, request.user, 'sale') #Parse the POST into an ExchangeCluster
    
    form = MainPOSForm()
    
    item_forms = [ BeverageSaleForm(prefix='beverage'), ComputerRentalForm(prefix='computer_rental') ]
    
    sales = BeverageInstance.objects.order_by('created')[:10].reverse() #Show the last 10 beverage sales
    return render(request, 'pos/beverage_sale.html', locals())


#Let's give formsets a try - can we make them work dynamically?
#(Early answer appears to be "maybe" - they iterate fine in the template but then get a bit goofy on the other side during validation)


def record_donation(request):
    
    main_form = DonationForm()
    MoneyFormSet = formset_factory(SimpleMoneyForm)(prefix="Money")
    transaction_type = 'donation'
    
    
    if request.POST:
        #They are issuing a POST.  Let's handle it and create the record of this new donation.
        #(or send them back to the form to correct errors if there are any)
        exchange = donation_from_POST(request.POST, request.user.member)
        return HttpResponse('Donation recorded.')
        
#        if not invalid:
#            pass
#        
#        else:
#            form = invalid
#            return render(request, 'commerce/record_transaction.html', locals())
        
    else:
        #They are brand new to this page.  Give them the form they are looking for.
        

        #In some cases, we'll need to enter a completely new user. Let's prepare forms for that.
        contact_forms = UserContactForm(prefix="user"), UserContactInfoForm(prefix="contact"), UserProfileForm(prefix="profile")
    
        #We want email, first name, and last name to be required for all submissions.
        contact_forms[0].fields['email'].required = True
        contact_forms[0].fields['first_name'].required = True
        contact_forms[0].fields['last_name'].required = True
        #No phone needed.
        contact_forms[1].fields['phone'].required = False
        
        MoneyFormSet = formset_factory(SimpleMoneyForm)(prefix="Money")
        RealThingFormSet = formset_factory(DonationRealThingForm)(prefix="Real Things")
        
        item_forms = [MoneyFormSet, RealThingFormSet]

        return render(request, 'commerce/record_transaction.html', locals())

def view_exchange(request, id):
    exchange = Exchange.objects.get(id=id)
    return render(request, 'commerce/view_exchange.html', locals())

def view_purchase(request, seller_involvement_id):
    involvement = ExchangeInvolvement.objects.get(id=seller_involvement_id)
    return render(request, 'commerce/view_purchase.html', locals())

def view_pledge(request, pledge_id):
    pledge = Pledge.objects.get(id=pledge_id)
    return render(request, 'commerce/view_pledge.html', locals())

def list_purchases(request, party_id):
    party = GenericParty.objects.get(id=party_id).lookup()
    purchases = ExchangeInvolvement.objects.filter(party=party)
    return render(request, 'commerce/list_purchases.html', locals())
    


def individual_delivery(request):
    big_index_list = []
    for item in request.POST: #item will look something like "delivery_104"
        if item.split('_')[0] == 'deliver':
            pledge_id = item.split('_')[1]
            pledge = Pledge.objects.get(id=pledge_id)
            valid, delivery, index_list = pledge.deliver(ingredient_index=True)
            big_index_list.append(index_list)
    return render(request, 'commerce/individual_delivery_result.html', locals())

def eshu_main(request):
    
    return render(request, 'eshu/main.html', locals())


def fluidbarter_main(request):
    
    test_message = 'Hello World'
    
    return render(request, 'commerce/fluidbarter_landing.html', locals())
    
