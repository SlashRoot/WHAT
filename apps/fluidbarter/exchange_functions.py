  
from fluidbarter.models import ReceiptFile, RealThingSize, ExchangeInvolvement, MoneyBag, MoneyBagPiece, Exchange, PaymentMethod, Pledge    
from people.models import GenericParty    
    
def exchange_between_two_parties(seller, buyer, user, receipt_image=None, date=None):
    '''
    Dehydration Function.
    
    Takes the name of some other party and some member, and returns the following in a tuple:
    
    *an exchange object
    *the other party's involvement object
    *our involvement object
    '''    
    
    if receipt_image:
        receipt = ReceiptFile.objects.create(file=receipt_image)
        exchange = Exchange.objects.create(manager=user, invoice_data=receipt)
        
    else:
        exchange = Exchange.objects.create(manager=user)
        
    if date:
        exchange.start_date = date
        exchange.save()
    

    seller_involvement = ExchangeInvolvement.objects.create(exchange = exchange, party = seller )
    buyer_involvement = ExchangeInvolvement.objects.create(exchange = exchange, party = buyer )
    
    return exchange, seller_involvement, buyer_involvement

def pledges_from_involvements(buyer_involvement=None, seller_involvement=None):
    '''
    Dehydration Function.
    
    Creates symmetrical pledges and adds them to their respective involvements.
    '''
    seller_pledge = Pledge.objects.create(pursuant_to=seller_involvement, recipient=buyer_involvement)
    buyer_pledge = Pledge.objects.create(pursuant_to=buyer_involvement, recipient=seller_involvement)

    #This probably ought to be a function somewhere.
    seller_pledge.incoming_pledges.add(buyer_pledge)
    buyer_pledge.incoming_pledges.add(seller_pledge)
    
    return buyer_pledge, seller_pledge
              
def donation_from_POST(post, member):
    '''
    Takes a POST from the donation form, figures that shit out.
    '''
    donor = party_from_encrypted_string(post['lookup_other_party'])
    
    exchange, donor_involvement, our_involvement = exchange_with_other_party(donor, member)
    
    donor_pledge = Pledge(pursuant_to = donor_involvement, recipient=our_involvement)
    donor_pledge.save()  
    
    #Do I love these next 8 lines?  No.  No I do not.  -Justin
    try:
        num_money_bags = int(post['Money-TOTAL_FORMS'])
    except:
        num_money_bags = 0
        
    try:
        num_real_things = int(post['Money-TOTAL_FORMS'])
    except:
        num_real_things = 0

    for n in range(1, num_money_bags + 1):   
        method = PaymentMethod.objects.get(id=post['Money-' + str(n) + '-method'])
        amount = post['Money-' + str(n) + '-amount']
        money_bag = MoneyBag.objects.create(method = method)
        piece = MoneyBagPiece.objects.create(money_bag = money_bag, amount = amount)
        
        #Add this money bag as an item in the donor's involvement.
        donor_pledge.items.add(piece)
        donor_pledge.save()
        
    #TODO: Hook up real-thing donations
    
    donor_pledge.deliver()

    return exchange


def buy_item(group=False,
             deliver=False,
             seller_involvement=None,
             buyer_involvement=None,
             trade_element=None,
             trade_element_kwargs=None,
             money_bag=None,
             price=None,
             quantity=None,
             ):
    '''
    A dehydration method specially for trading a real thing for a money bag.
    Returns a tuple of seller Pledge and buyer Pledge.
    
    Pledges will be delivered if deliver=True.
    If quantity is more than one, items will each be assigned their own pledge unless group=True.
    '''
    if group:
        buyer_pledge, seller_pledge = pledges_from_involvements(buyer_involvement=buyer_involvement, seller_involvement=seller_involvement)

    for counter in range(quantity): #We'll iterate through once for each item in the quantity.
        if not group:  # We didn't get the pledges above, so we'll need to get them for each item now.
            buyer_pledge, seller_pledge = pledges_from_involvements(buyer_involvement=buyer_involvement, seller_involvement=seller_involvement)
        
        #Get the size details
        try:
            quantification_method = trade_element_kwargs.pop('unit of quantification')
            amount = trade_element_kwargs.pop('amount')
        except:
            #Guess they don't have an amount for their quantification method.
            #TODO: Neaten this.
            pass

        # Make the thing
        # The kwargs will have come most recently from get_purchase_details, which in turns gets them from a form.
        real_thing = trade_element.objects.create(**trade_element_kwargs)
        
        try:
            property = trade_element_kwargs.pop('property')
            if property:
                real_thing.properties.add(property)
        except:
            #TODO: This is pretty lame. Property is supposed to be ManyToMany.
            pass 
        
        #Make and associate the size of the thing
        size = RealThingSize.objects.create(unit=quantification_method, number=amount, thing=real_thing)
        
        seller_pledge.items.add(real_thing)
        
        #..and we give them some money.
        piece = MoneyBagPiece.objects.create(money_bag = money_bag, amount = price)
        buyer_pledge.items.add(piece)
        
        #Deliver both.
        #TODO: Add shipping tracking here.
        if deliver:
            seller_pledge.deliver()
            buyer_pledge.deliver(change_owner=True)
            
    return seller_pledge, buyer_pledge
        
    

def get_purchase_details(main_form, item_forms, user, buyer_group=None, receipt_image=None, date=None):    
    '''
    Takes the following:
    
    *A main_form, which has information about the overall puchase.
    *item_forms, each of which should a tuple of a formset and a model
    *buyer_group - A Group who is the buyer.  Otherwise the buyer is the user.
    *user - the group member who is entering the transaction
    *deliver - a boolean about whether delivery has yet been made.
    
    TODO: Fix and finish.
    TODO: Ensure that the user is in fact a member of buyer_group
    '''
    
    if buyer_group:
        buyer_party = GenericParty.objects.get(group=buyer_group)
    else:
        buyer_party = GenericParty.objects.get(user=user)
    
    houston_we_have_a_problem = False if main_form.is_valid() else True
    
    #We have more than one formset (call it a formset-set) - let's check each one.
    for bound_formset, model in item_forms:    
        if not bound_formset.is_valid():
            houston_we_have_a_problem = True            
    
    if houston_we_have_a_problem:
        #We have a problem.  Tell them so and spit back the forms.
        return False, (main_form, item_forms)
        
    #Nothing seems to have caused a problem.  Proceed.    
    vendor = main_form.cleaned_data['other_party']
    
    exchange, vendor_involvement, our_involvement = exchange_between_two_parties(vendor, buyer_party, user, receipt_image=receipt_image, date=date)
    
    SlashRoot = our_involvement.party
    
    
    #For the moment, we're assuming that the first formset is device, the second is item, the third is ingredient.
        
    #Assume this is one money bag for the entire purchase.
    method = main_form.cleaned_data['payment_method']    
    money_bag = MoneyBag.objects.create(method = method)
    
    
    
    for formset, model in item_forms:
        #Each formset is for a type of purchase (device, ingredient, etc)
        #So, within this loop, we're dealing with a formset which contains one form for each item purchased.
    
        for form in formset:
            #First we need to actually instantiate the device (assume, for a moment, that this device is not yet in our ecosystem)
            #TODO: Review this code to ensure that devices (or, for that matter, other objects) can't get created only to be thwarted by some error or odd circumstance further down in the code.
    
            try:
                #Copy the cleaned data into a dict
                purchase_form_dict = form.cleaned_data.copy()
                
                #Pop four important pieces of information out of the dict
                quantity = purchase_form_dict.pop('quantity')
                price = purchase_form_dict.pop('price_per')
                deliver = purchase_form_dict.pop('deliver')
                group = purchase_form_dict.pop('group')
                
                #This is standard (we are the new owner)
                standard_trade_element_dict = {
                                      #I guess there's nothing left here.
                                      #TODO: Examine if this dict is still needed.
                                      }
                
                #Merge what's left of the popped dict into the standard dict and we have our kwargs.
                trade_element_dict = dict(standard_trade_element_dict, **purchase_form_dict)
            
            except KeyError:
                #TODO: Figure out why some forms come in blank (and thus produce KeyError)
                continue
    
            vendor_pledge, our_pledge = buy_item(
                     seller_involvement = vendor_involvement, 
                     buyer_involvement = our_involvement,
                     trade_element = model,
                     trade_element_kwargs = trade_element_dict,
                     price = price,
                     money_bag = money_bag,
                     quantity = quantity,   
                     deliver = deliver,
                     group = group,
                     )
    return True, [vendor_involvement, our_involvement]
