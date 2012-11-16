from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from what_apps.commerce.models import TradeElement, RealThing


class IngredientInventoryIndex(models.Model):
    '''
    A model whose only job is to maintain the lowest number assignable to current inventory items.
    '''
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return str(self.id)

def get_next_inventory_index():
    available = IngredientInventoryIndex.objects.exclude(stockitem__depleted = None)
    
    try:
        next = available[0]
    except IndexError:
        next = IngredientInventoryIndex.objects.create()        
    return next


class ProductBrand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    maker = models.ForeignKey('people.CommerceGroup')

    def __unicode__(self):
        return self.name

    
class Product(TradeElement): #Ethereal
    '''  
    A Product in general that we offer for sale, such as Cappucino or USB Thumb Drives.
    This is NOT a specific "Joe's Cappucino" or "That USB Thumb Drive that Mary is using right now."
    '''

    
    
    def __unicode__(self):
        return self.name
    

class Ingredient(Product): #Ethereal
    '''
    An ingredient that we use.
    
    Possible interesting info:
    *Seasonal availability
    *Medicinal value
    *Taste qualities
    *Ingredients that play nice (or not nice) with self
    '''
    
    def __unicode__(self):
        return self.name
    
    
class IngredientProperty(models.Model): #Semi-ethereal
    '''
    An abstraction model to describe an etheral quality in a general for a specific ingredient.
    The canonical case is fat content in milk.
    
    Other possibilies include whether peanut butter is salted or not, etc.
    '''
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name

class IngredientStock(RealThing): #Literal
    '''
    This is a specific ingredient in stock, like a jar of peanut butter.
    
    It may be counter-intuitive to think of this as exclusively a ContractItem, but I think it is.
    Even if we pick it from a field, that's a contract with nature.  The other party (the field) has what we might call contact information - an address at least.
    The contract has a date on which it occured and a manager (the picker or person entering it).
    '''
    brand=models.ForeignKey(ProductBrand)
    created=models.DateTimeField(auto_now_add=True)
    depleted=models.DateTimeField(blank=True, null=True)
    ingredient = models.ForeignKey(Ingredient)
    index = models.ForeignKey(IngredientInventoryIndex, related_name="stockitem", blank=True, null=True)
    properties = models.ManyToManyField(IngredientProperty)
    
    def size_display(self):
        if self.size == 3780:
            return "Gallon"
        if self.size == 1890:
            return "Half-Gallon"
        if self.size == 473:
            return "Pint"
        
        return str(self.size)
    
    def assign_ingredient_index(self):
        self.index = get_next_inventory_index()
        self.save()
        
        return self.index
    
    def __unicode__(self):
        #TODO: Properties is ManyToMany.  Live it.
        try:
            return self.index + ": " + self.brand + " " + self.ingredient + " (" + self.properties.all()[0] + ")"
        except:
            return self.ingredient.name
        
    def character(self):
        '''
        Characteristics to determine if this item is similar enough to another item to group their pledges together on an invoice.
        
        For example, we can group milk objects together if they're the same brand and the same fat content.
        
        For the purposes of determining similarity in a pledge, we consider both the item pledged and the amount of the incoming pledge.
        '''
        so_far = str(self.size.all()[0].number) + " " + str(self.size.all()[0].unit.abbreviation) + " " + str(self.brand.name) + ", " + str(self.ingredient.name)
        for property in self.properties.all():
            so_far += " (" + str(property.name) + ")"
        
        return so_far            
    
def index_ingredient(sender, **kwargs):
    index = get_next_inventory_index()
    sender.inventory_index = index
    
pre_save.connect(index_ingredient, sender=IngredientStock)    
        

class Beverage(Product): #Ethereal
    '''
    A beverage that we offer for sale, such as coffee or Jason's Mountain Mix.
    This is NOT a specific beverage that we are selling right now, such as "Suzie's Coffee that she bought on Friday."
    '''
    
    ingredients=models.ManyToManyField(Ingredient, related_name="products", blank=True, null=True)
    inventor=models.ForeignKey(User, blank=True, null=True)
    directions=models.TextField(blank=True, null=True)
    #tags
        
    def __unicode__(self):
        return self.name  


class Cup(models.Model):
    size=models.IntegerField()
    created=models.DateTimeField(auto_now_add=True)
    description=models.TextField(blank=True, null=True)
    #TODO: This might want other fields, such as: creator, color, quick_id (oh boy!), tags, owner, handle (bool),  



class BeverageInstance(RealThing): #Literal
    cup = models.ForeignKey(Cup)
    ingredients = models.ManyToManyField('products.IngredientStock', blank=True, null=True)
    beverage = models.ForeignKey(Beverage)
    barista = models.ForeignKey(User)
    
    def get_element(self):
        return self.beverage





class ConsignmentItem(Product): #Ethereal
    wholesaler=models.ForeignKey(User)
    wholesale_price=models.FloatField()
    
class ConsignmentItemStock(RealThing): #Literal
    item = models.ForeignKey(ConsignmentItem)



class ComputerRental(Product): #Literal
    #TODO: PLACE IN LITERAL FAMILY
    computer=models.ForeignKey('hwtrack.Computer', related_name="public_uses")
    ending_time=models.DateTimeField(blank=True, null=True)
    price=models.FloatField()



