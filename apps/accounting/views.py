# Create your views here.
from django.shortcuts import render_to_response, render 
from django.db.models import Avg

from contact.forms import UserContactForm, UserContactInfoForm, UserProfileForm, handle_user_profile_form

from models import Projection

from commerce.models import Exchange, ExchangeInvolvement, RealThing

from people.models import CommerceGroup
        

def show_donations(request):
    SlashRoot = CommerceGroup.objects.get(id=114)
    
    #What is a 'donation'?  
    #For our purposes, it's every exchange we've been involved in where we haven't pledged anything.
    our_involvements = SlashRoot.exchanges.filter(pledged=None) 
    
    donations = []
    
    for involvement in our_involvements:
        others = involvement.other_involvements()
        for involvement in others: #Iterate through each other party
            amount = involvement.amount_pledged()
            donation = {'amount' : amount, 'donor' : involvement.party }
            donations.append(donation)
    
    return render(request, 'accounting/show_donations.html', locals())


'''
Not sure where Dominick was going with these.
'''


#def Income(request):
#    
#    categories = Projection.objects.all()
#    
#    total = Projection.objects.aggregate(Avg('credit'))
#    
#    return render ('numbers.html', locals())
#
#def Expenses(request):
#    
#    categories = Projection.objects.all()
#    
#    total = Projection.objects.aggregate(Avg('debit'))
#    
#    return render ('numbers.html', locals())