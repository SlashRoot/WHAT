from django import forms

from people.models import Role, Group, RoleInGroup, UserInGroup
from utility.forms import AutoCompleteField

from django.contrib.auth.models import User
        
class UserInGroupForm(forms.Form):
    user = AutoCompleteField(label="User", models=([User,'first_name'],))
    role = forms.ModelChoiceField(Role.objects.all())
    group = forms.ModelChoiceField(Group.objects.all())
    
    def save(self):
        '''
        Given validated data, gets_or_creates a RoleInGroup.
        Assigns user to that RoleInGroup.
        
        Returns boolean for whether RoleInGroup was created
        '''
        try:
            user = self.cleaned_data['user']
            role = self.cleaned_data['role']
            group = self.cleaned_data['group']
        except (KeyError, AttributeError), e:
            raise TypeError('You must validate this form before saving the underlying objects.')
        
        role_in_group, is_new = RoleInGroup.objects.get_or_create(role=role, group=group)
        user_in_group = UserInGroup.objects.create(role=role_in_group, user=user)
        
        return is_new


