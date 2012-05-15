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
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            role = form.cleaned_data['role']
            group = form.cleaned_data['group']
            send_to_higher_roles = form.cleaned_data['send_to_higher_roles']
            
            ## Step two: Piece the data together to form a message
            blast_message = "To " + role + group + ":" + "\n" + message ## Result Example: To Keeper in Slashroot: (next line) Hello Keeper in Slashroot! How are you?
            
            ## Step three: Send the data out. Take notice that blast_message is being used rather than just message.
            ##TODO: I've set up the structure for this form to work. Now we need to figure out how to gather email information because this will not work at all.
            send_mail(subject, blast_message, 'dpiaquadio@gmail.com', group)
            
            return HTTPResponseRedirect('/blast_form/confirmation/')
        else:
            form = BlastMessageForm()
    else:
        form = BlastMessageForm()
    
    return render(request,'email_blast/email_blast_form.html',locals())