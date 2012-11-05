from .forms import UserInGroupForm
from .models import Role, Group, RoleInGroup, UserInGroup
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import json


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
            return HttpResponseRedirect('/people/awesome/')
    else:
        user_in_group_form = UserInGroupForm()
        
    return render(request, 'people/role_form.html', locals())

def awesome_o(request):
    return render(request, 'people/awesome.html', locals())

def membership_roles(request):
    roles = Role.objects.all()
    groups = Group.objects.all()
    
    roles_in_groups = RoleInGroup.objects.filter(id=groups)
    users_in_group_with_roles = UserInGroup.objects.filter(id=roles_in_groups)
    
    return render(request, 'people/membership_roles.html', )
    