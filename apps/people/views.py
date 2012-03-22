from django.contrib.auth.models import User
from django.shortcuts import render 
from django.http import HttpResponse

import json

from django.contrib.auth.decorators import login_required

@login_required
def who_am_i(request):
    
    validating_user = {'username': request.user.username}
    
    confirmation = json.dumps(validating_user)
    
    return HttpResponse(confirmation)

