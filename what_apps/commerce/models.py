from django.db import models
from django.db.models import Sum, Variance
from django.core.exceptions import ValidationError

from what_apps.utility.models import GenericPartyForeignKey

'''
This app covers three major types of knowledge:

1. What: The stuff we buy and sell.
2. How: The terms and occasions under which we buy and sell.
3. When and Where: Delivery of items between parties.

The "who" is covered in people.
The "why" is in accounting.


CHAPTER ONE: What
'''

class BudgetLinePerspective(models.Model):
    '''
    The budget lines into which items in a particular trade category fall from the perspective of a particular party.
    
    For example, for us, the trade category "computer hardware" might be on the incoming budget line "hardware aquisition" and the outgoing budget line "hardware retail."
    '''
    trade_element = models.ForeignKey('commerce.TradeElement', related_name="budget_perspectives")
    incoming_budget_line = models.ForeignKey('accounting.BudgetLine', related_name="incoming_perspectives")
    outgoing_budget_line = models.ForeignKey('accounting.BudgetLine', related_name="outgoing_perspectives")
    
    class Meta:
        unique_together = ['trade_element', 'incoming_budget_line', 'outgoing_budget_line']

class BudgetPerspective(models.Model):
    '''
    Together, these TradeCategoryPerspectives form an entire BudgetPerspective.
    
    Perhaps interesting BudgetPerspectives can be shared.
    '''
    budget_lines = models.ManyToManyField('commerce.BudgetLinePerspective')
    #TODO: Perhaps a creator in the form of the organization who coined it?    
        
class TradeElement(models.Model): #Ethereal
    """
    Specific products or services that we offer for sale or seek for purchase.
    
    ie French Roasted Coffee, Cafe Latte, Ubuntu Installation, Acme A451 2TB Hard Drives, etc.
    
    All of our products and services are children of this model.
    """
    
    name = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True, help_text="The datetime that the object was created." )
    description = models.TextField(blank=True, null=True)   
    
    def __unicode__(self): 
        return self.name 
    
class TradeElementProgeny(models.Model):
    child = models.ForeignKey(TradeElement, related_name="parents")
    parent = models.ForeignKey(TradeElement, related_name="children")

class TradeItem(models.Model): #Literal
    '''
    A single instance of a thing that exists in the universe that we are buying, selling, or trading right now.
    ie, a sum of money, a cup of coffee, a computer, an hour of service, etc.
    '''
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def drill_down(self):
        '''
        Stupid and hopefully temporary.  Some of the worst code of my life in this function here.
        
        TODO: Unstupify.
        
        See http://stackoverflow.com/questions/5348157/find-object-in-child-class-from-object-in-parent-class-in-django
        '''
        try:             
            return self.moneybagpiece
        except:
            try:
                return self.realthing.ingredientstock
            except:
                try:
                    return self.realthing.device
                except:
                    return self.realthing
            

    '''
    You'd think relating to element would be, well, elemental.
    But it turns out not to be.  Instead, we have literal and ethereal versions
    of our products and services as subclasses, and then get down with one another directly.
    '''
    #element = models.ForeignKey(TradeElement) #Keep this line as a reminder
    
class RealThing(TradeItem): #Literal
    ''' 
    A TradeItem that is not currency.
    '''
    name = models.CharField(max_length=80, blank=True, null=True)
    
#    def __unicode__(self):
#        return self.name
        #Something interesting here
    
    def character(self):
        '''
        Characteristics to determine if this item is similar enough to another item to group their pledges together on an invoice.
        
        For example, we can group milk objects together if they're the same brand and the same fat content.
        '''
        return self.name
        
    
class MoneyBag(models.Model): #Literal
    '''
    A distinct pile of money.  ie, the $27.51 that Joe spent at the grocery store.
    
    We'll ForeignKey to the TradeElement entry for whatever type of currency this is.
    
    (Now split into several "pieces" - see below.)
    '''
    currency = models.ForeignKey('commerce.TradeElement', default=1)
    method = models.ForeignKey('PaymentMethod')
    
    def amount(self):
        return self.pieces.aggregate(Sum('amount'))


class MoneyBagPiece(TradeItem):
    '''
    A piece of that same moneybag - the $2.71 that Joe spent on spam during his trip to the grocery store.
    '''
    money_bag = models.ForeignKey('commerce.MoneyBag', related_name="pieces")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    
    def __unicode__(self):
        return str(self.amount)
    
    def character(self):
        return str(self.amount) 


class PaymentMethod(models.Model):
    '''
    A method of delivery currency - ie cash, check, card, etc.
    '''
    name = models.CharField(max_length=30)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name


class QuantificationUnit(models.Model):
    '''
    Oz, mL, megabytes, inches, etc.
    '''
    name = models.CharField(max_length=30)
    abbreviation = models.CharField(max_length=5)
    description = models.TextField()
    dimension = models.ForeignKey('QuantificationDimension')
    
    def __unicode__(self):
        return self.abbreviation

    
class QuantificationDimension(models.Model):
    '''
    What dimension are we quantifying?  Height? Volume? Weight? Size? Count? Storage Capacity?
    '''
    name = models.CharField(max_length=30)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name

    
class QuantificationRatio(models.Model):
    '''
    The ratio between two quantification units.
    '''
    smaller_unit = models.ForeignKey(QuantificationUnit, related_name="larger_units")
    larger_unit = models.ForeignKey(QuantificationUnit, related_name="smaller_units")
    ratio = models.FloatField(help_text="How many of the smaller unit does it take to get one of the larger unit?")


class RealThingSize(models.Model): #Literal
    '''
    Any actual instance of quantity of some object.
    '''
    unit = models.ForeignKey(QuantificationUnit)
    number = models.DecimalField(max_digits=8, decimal_places=2)
    thing = models.ForeignKey('commerce.RealThing', related_name="size")

'''
CHAPTER TWO: CONTRACTS AND EXCHANGES (How)
'''

class Pledge(models.Model):
    '''
    A single party pledging a particular item as part of their involvement in an exchange.
    
    This object relates to ExchangeInvovlement twice: 
    1) for the party doing the pledging and 
    2) for the party receiving the item being pledged.
    
    Think of this as similar knowledge to that which is needed to win the game of Clue:
    "Mr. Plum gave Miss Scarlet the Candlestick in Exchange #44"
    (That sounded dirty - I really didn't mean it to :-))
    
    This model also tracks what the pledger is getting in exchange for their pledge via a self-pointing ManyToMany.
    '''
    
    #What items are being offered?
    items = models.ManyToManyField('TradeItem', related_name="Trades")
    
    #As part of what exchange involvement?
    pursuant_to = models.ForeignKey('ExchangeInvolvement', related_name="pledged")
    
    #What, if anything, do we expect in return?
    incoming_pledges = models.ManyToManyField('Pledge', symmetrical=False, blank=True, null=True)
    
    #Somebody is getting whatever is being pledged.  We'll point to their involvement in this exchange.
    recipient = models.ForeignKey('ExchangeInvolvement', related_name="owed")
    
    
    def deliver(self, change_owner=False, ingredient_index=False):
        '''
        Conveinence method for delivering on this pledge. 
        Useful if no details about the delivery are needed, such as a coffee sale.
        
        In the example of a coffee sale, we don't bother assigning an owner.  Nobody cares who owns a cup of coffee.
        '''
        from what_apps.commerce.models import Delivery, Ownership #Fucked up.  I do not understand why this line is needed or throws an error in PyDev.
        new, delivery = Delivery.objects.get_or_create(pledge=self)
        
        if not new:
            return False, delivery
        
        #if change_owner:
            #Loop through each item in this pledge and create a new ownerhsip object.
         #   for thing in self.items.all():
          #      if RealThing in thing.__class__.__bases__: #We only want to own realthings.
           #         Ownership.objects.create(realthing=thing, owner = GenericParty.objects.get(party=self.recipient.party))
        
        if ingredient_index: #We need to assign (and return) ingredient indices for each item that is an ingredient.
            index_list = []
            for item in self.drill_down():
                try:
                    index = item.assign_ingredient_index()
                    index_list.append((item, index))                                                        
                except AttributeError:
                    pass
            
            return True, delivery, index_list
            
        
        return True, delivery
        
    def amount(self):
        currency_items = self.items.exclude(moneybagpiece=None) #Get all the items that are MoneyBagPiece objects 
        amount = currency_items.aggregate(Sum('moneybagpiece__amount'))['moneybagpiece__amount__sum']
        return amount
    
    def incoming_amount(self):
        total = 0
        for p in self.incoming_pledges.all():
            total += p.amount()
        return total
    
    def first_incoming_item(self):
        '''
        Returns the drill-down of the first incoming item.
        '''
        first_incoming_pledge = self.incoming_pledges.all()[0]
        first_item = first_incoming_pledge.items.all()[0]
        return first_item.drill_down()
    
    def first_outgoing_item(self):
        '''
        Returns the drill-down of the first outgoing item.
        '''
        first_item = self.items.all()[0]
        return first_item.drill_down()            
    
    def first_incoming_item_amount(self):
        '''
        Assumes first item is a MoneyBagPiece.
        TODO: Handle other cases intelligently.
        One idea is to make this function more broad, giving the amount of whichever first incoming item is a MoneyBagPiece (incoming or outgoing).
        Of course, in this case, we'll need to gracefully handle an exception if it's a barter.
        '''
        return self.first_incoming_item().amount
    
    def drill_down(self):
        '''
        Get the drilled-down items in this pledge and return them as a list.
        '''
        items = []    
        for item in self.items.all(): #Go through each item in the pledge
            items.append(item.drill_down()) #Append the drill_down result to the list
        return items
    
    def character(self):
        '''
        Get the character of each drilled-down item for the purposes of telling if this pledge's items are exactly the same as another's.
        '''
        try: #This branch will work if the items are all RealThings.
            so_far = ""
            for item in self.drill_down():
                so_far += item.character() + " "
                
            for p in self.incoming_pledges.all():
                so_far += " " + str(p.amount())
                            
        
        except AttributeError: #This branch will work if the items are all MoneyBags.
            so_far = 0
            for item in self.drill_down():
                so_far += item.amount()
                
        return so_far
    
    def is_homogenous(self):
        homogenous = True
        match = self.drill_down()[0].character()         
        for item in self.drill_down():
            homogenous = True if item.character() == match else False
        
        return homogenous
    
    def group(self):
        '''
        We call a pledge a 'group' if:
        1) It has more than one item
        2) It is homogenous
        '''
        if self.is_homogenous() and self.items.count() > 1:
            group = {
                     'display': self.first_outgoing_item().character(),
                     'quantity': self.items.count(),
                     'price_per': self.first_incoming_item_amount(),
                     }
            return group
            
        else:
            return False
        
    def __unicode__(self):
        so_far = ""
        for item in self.drill_down():
            so_far += item.character() + " "
            
        return so_far

    

class ExchangeInvolvement(models.Model):
    '''
    A single party's involvement in an entire exchange.  
    In a sense, this is a through model from party to exchange, although not coded that way.
    Interestingly, we have Pledge relating to this object twice - see the docstring in Pledge for details.
    First, all pledges are pursuant to some ExchangeInvolvement object.  ie, Why did 
    '''
    #Whose invovlement are we talking about?
    #(ie, who is the party? Likely a person or CommerceGroup, such as a company)
    party = GenericPartyForeignKey()
    
    #In what exchange?
    exchange = models.ForeignKey('Exchange', related_name="parties")
    
    def slashroot_as_party(self):
        '''
        Conveinence method for setting SlashRoot as the party.
        Does not save.
        '''
        self.party = SLASHROOT_AS_GENERICPARTY
    
    def get_other_involvements(self):
        '''
        Returns a tuple consisting of:
        (if the exchange is two-party)
        *True
        *The object of the other party
        
        (if not)
        *False
        *A queryset of the other parties
        
        For example, in a sale, if we have our involvement, this will give us the customer's involvement.        
        '''        
        other_parties = self.exchange.parties.exclude(commercegroup=self.party)
        
        if len(other_parties) == 1:
            two_way = True
            party_info = other_parties[0]
        else:
            two_way = False
            party_info = other_parties
        
        return two_way, party_info
    
    def amount(self):
        currency_pledges = self.pledged.exclude(items__moneybagpiece=None)
        amount = currency_pledges.aggregate(Sum('items__moneybagpiece__amount'))['items__moneybagpiece__amount__sum']
        return amount
    
    def characters(self):
        '''
        Return the characters of all pledges as a list
        '''
        list_of_characters = []
        
        for pledge in self.pledged.all(): #Go through each pledge
            if pledge.character() not in list_of_characters:
                list_of_characters.append(pledge.character())
        
        return list_of_characters
    
    def get_pledge_clusters(self):
        '''
        Cluster all pledges which are for the same item.
        (ie, if we buy 6 half-gallons of Organic Cow Whole Milk in the same exchange, get all six of those pledges).
        '''
        
        grouped_pledges = {}
        
        for pledge in self.pledged.all():
            if pledge.character() in grouped_pledges:
                grouped_pledges[pledge.character()][1].append(pledge) #Increase the number of pledges in the group
                
            else:
                grouped_pledges[pledge.character()] = [pledge.__unicode__(), [pledge], 0]
                
            for p in pledge.incoming_pledges.all():                
                grouped_pledges[pledge.character()][2] += p.amount()
        
        return grouped_pledges
    
    
    def __unicode__(self):
        return "Involvement of " + self.party.lookup().get_full_name() + " in Exchange #" + str(self.exchange.id)
    


class Exchange(models.Model):
    '''
    THIS IS THE MAJOR CLASS HERE PEOPLE. It may not look big, but everything points here.
    
    This is an entire exchange.  It may be between two or more parties, each of whom will connect via a ForeignKey in ExchangeInvolvement.
    '''    
    #When dealing with exchanges of RealThings that have TradeElements, we'll grab the budget line from there.
    #Otherwise, we'll need to specify it.
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now_add=True)
    manager = models.ForeignKey('auth.User', related_name="managed_exchanges") #Who handled this Exchange?
    invoice_data = models.ForeignKey('InvoiceData', blank = True, null = True)
    
    def list_parties_as_string(self):
        list_of_parties = []
        for involvement in self.parties.all():
            party = involvement.party.lookup()
            list_of_parties.append(party)
            
        return list_of_parties
    


class InvoiceData(models.Model):
    '''
    A receipt, either paper or electronic
    '''
    pass

class ReceiptFile(InvoiceData):
    '''
    A receipt in the form of a file.  Maybe paper, maybe HTML.
    '''
    file = models.FileField(upload_to = 'static/uploaded/receipts',)

        
'''
CHAPTER THREE: TRANSACTIONS (When, Where and with Whom)
'''

class Delivery(models.Model):
    '''
    Delivery of a particular item (which is specified in a child class).  
    ie, us paying a bill or a customer paying us for coffee or computer service.
    
    (Note that most exchanges are two or more deliveries - one for each item)
    '''
    created = models.DateTimeField(auto_now_add=True)
    pledge = models.OneToOneField(Pledge, related_name="delivery")
    


class Shipping(Delivery):
    '''
    A delivery whose means are via a shipping carrier.  
    '''
    pass


class Bill(models.Model):
    '''
    Pretty sure we all know what a bill is.
    '''
    created = models.DateTimeField(auto_now_add=True, help_text="The moment this object was created.")
    period_start = models.DateTimeField(help_text="The beginning of the billing period.")
    period_end = models.DateTimeField(help_text="The end of the billing period.")
    date = models.DateTimeField(help_text="The date printed on the bill.")
    due_date = models.DateTimeField(help_text="The due date of the bill.")
    pledge = models.ForeignKey('commerce.Pledge')
   
class Custody(models.Model): 
    '''
    Who is the bearer of a RealThing?
    Has it changed at all since last Spring?
    Who owns the foo, the bar and the bing?
    "I own the crown," chimed in the king.
    
    But when custody changes, a new instance we'll make
    of this very model, and then we'll eat cake
    for trading with friends is some give and some take
    I give you some string, you give me a rake
    
    Bearers can be either users or parties
    they can be very small or be very hardy
    their name can be joe, mary, susan, or marty
    but they certainly must be users or parties   
    
    The Bearer may own the RealThing in question
    and their name might be Lary, Lisa, or Sebastchain 
    If they own it the Boolean will be True
    as long as they didn't steal it from you.
    '''
    
    created = models.DateTimeField(auto_now_add=True)
    realthing = models.ForeignKey('commerce.RealThing')
    bearer = GenericPartyForeignKey()
    ownership = models.BooleanField()
 