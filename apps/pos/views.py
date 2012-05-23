from django.http import HttpResponse as response, HttpResponseRedirect
from django.shortcuts import render_to_response as render
from django.template import loader, Context, RequestContext

from django.utils import simplejson as json
from hwtrack.models import Device
from django.db.models import Q

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

import stomp

#from haystack.query import SearchQuerySet


from products.models import Product, Beverage, Ingredient, BeverageInstance
from pos.forms import BeverageSalesForm

#from forms import QuickBeverageSaleForm


def bar_menu(request):
        categories = Ingredient.objects.filter(name='Coffee')
        products = Beverage.objects.filter(ingredients__name='Coffee')

        return render("test.html", locals())
    
#def barMenuRight(request):
#        categories = Ingredient.objects.filter(name='Tea')
#        products = Beverage.objects.filter(ingredients__name='Tea')
#
#        return render("test.html", locals())
#NOTE: The POS modal is not loaded by ajax.  It loads automatically when a member logs in.
#See main.views
#TODO: Update this when we move the POS modal to its final resting place


def beverageSale(request):
    '''
    I have a feeling that this function is going to become something of a boilerplate for ajax / autocomplete submissions.
    '''
    
    #Here's how we'll do the equivalent of form cleaning.
    member_bad=0
    beverage_bad=0
    milk_bad=0
    total_bad=0
    
    try:    
        member_id = request.POST['member'].split('-')[0]
        member = Member.objects.get(id=member_id)
    except:
        member_bad = 1
    
    try:
        product_id = request.POST['beverage'].split('-')[0]
        product = Beverage.objects.get(id=product_id)
    except:
        beverage_bad = 1
    
    
    try:
        milk_id = request.POST['milk'].split('/')[0]
        milk = Milk.objects.get(id=milk_id)
        
    except:
        milk_bad = 1
        
    #If they entered no milk at all, assume this is a no-milk drink.
    if request.POST['milk'] == "":
        milk_bad = 0
        milk = None
    
    try:
        total=float(request.POST['total'])
    except:
        total_bad = 1
        
        
        
    if member_bad + milk_bad + total_bad + beverage_bad > 0: #ie, the 'form' is not 'valid'
        
        bad_dict = {
                    'id_member':member_bad,
                    'id_beverage':beverage_bad,
                    'id_milk':milk_bad,
                    'id_total':total_bad,
                    }
        return response(json.dumps(bad_dict))
    
    #If we're all good....
    sale=BeverageSale(
                      member=member,
                      beverage=product,
                      cup=Cup.objects.get(id=1),
                      total=total,
                      milk=milk
                      )
    sale.save()
    
    conn = stomp.Connection()
    conn.start()
    conn.connect()
    
    t = loader.get_template('pos/sale_row.html')
    c = Context({'sale':sale})
    
    conn.send(t.render(c), destination="/pushFeeds/sales", dingo='llamas')

    
    
           
    return response(json.dumps(1))

def pos_landing(request):
    
    return render('pos/pos_landing.html', locals())

def sales(request):
    form = BeverageSalesForm(request.POST)
    return HttpResponseRedirect('/pos/')
    
    