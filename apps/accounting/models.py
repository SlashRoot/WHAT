from django.db import models

from mooncalendar.models import Moon
'''
Budgeting / Projections / Business Plan
'''


class BudgetCategory(models.Model):
    '''
    A bunch of budget lines - ie, "Administrative Costs" or "Beverage Income"
    '''
    name = models.CharField(max_length=30)
    description = models.TextField()
    '''
    #eliminated when justin realized that Trade Element has both an incoming and outgoing relation ship to Budget Line
    is_income = models.BooleanField() #Is this income or not? (If not, it's expense)
    
    '''
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Budget Categories"
    

class BudgetLine(models.Model):
    '''
    A single line in our budget - either income or expense.  IE, "Travel" or "Computer Service," or "Llama Food"
    '''
    name = models.CharField(max_length=30)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(BudgetCategory)
    
    def __unicode__(self): 
        return self.name 

class Projection(models.Model):
    '''
    A forecast of how much money we'll make or spend in a particular line during a particular moon.
    '''
    party = models.ForeignKey('people.GenericParty')
    budget_line = models.ForeignKey(BudgetLine)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    moon = models.ForeignKey(Moon)
 
