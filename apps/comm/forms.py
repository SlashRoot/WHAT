from django import forms

class ResolveCallsFilterForm(forms.Form):

    def __init__(self, caller_types, *args, **kwargs):
        self.fields = {}
        for c in caller_types:
            self.fields['%s_to' % c] = self.fields['%s_from' % c] = forms.BooleanField(required=False, initial=True)
            
        super(ResolveCallsFilterForm, self).__init__(args, kwargs)
        
        
        
        