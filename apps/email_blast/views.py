# Create your views here.
from django.core.mail import send_mail
from django.shortcuts import render

def email_blast(request):
    try:
        send_mail('Experiment One', 'Test.', 'glacierformdomino@hotmail.com',
                  ['dpiaquadio@gmail.com', 'glacierformdomino@hotmail.com', 'darkcatholic619@aol.com'], fail_silently=False)
    except:
        pass
    
    return render(request,'email_blast/email_blast_form.html',locals())