from checklist.models import Checklist
from checklist.models import Item
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

class ChecklistForm(forms.Form):
    pass

#for item in Item.objects.all()
#   ChecklistForm.base_fields['x'] = forms.CharField(...)   
    
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)

def checklistview(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ChecklistForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ChecklistForm() # An unbound form

    return render_to_response('checklist/checklist.html', {
        'form': form,
    })
    
def create_checklist(request):
    
    
def index(request):
    item_list = Item.objects.all()
    output = '<br/>'.join([x.Item for x in item_list])
    return HttpResponse(output)

