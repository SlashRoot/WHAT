from django.contrib.auth.models import User
from django.shortcuts import render 
from django.http import HttpResponse

import json

from django.contrib.auth.decorators import login_required
from people.forms import UserInGroupForm

@login_required
def who_am_i(request):
    
    validating_user = {'username': request.user.username}
    
    confirmation = json.dumps(validating_user)
    
    return HttpResponse(confirmation)
@login_required
def role_form(request):
    if request.method == 'POST':
        user_in_group_form = UserInGroupForm(request.POST)
            
        if user_in_group_form.is_valid():
            user_in_group_form.save()
    else:
        user_in_group_form = UserInGroupForm()
        
    return render(request, 'people/role_form.html', locals())