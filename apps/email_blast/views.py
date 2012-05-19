# Create your views here.
from django.core.mail import send_mail
from django.shortcuts import render

from email_blast.forms import BlastMessageForm

def email_blast(request):
    '''
Whenever members in roles within a group need notifications, they will receive a message
all at once in a blast instead of emailing to individual members within roles in a group.
-Dominick
'''
    ## Step one: Gathering Data
    if request.method == 'POST':
        form = BlastMessageForm(request.POST)
        if form.is_valid():
            form.instance.prepare()
            form.instance.send_blast()
            
            return HTTPResponseRedirect('/blast_form/confirmation/')
    else:
        form = BlastMessageForm()
    
    return render(request,'email_blast/email_blast_form.html',locals())