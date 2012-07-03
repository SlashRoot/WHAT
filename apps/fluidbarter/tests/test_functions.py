from fluidbarter.forms import PurchaseForm, THINGS_WE_PURCHASE
from django.forms.formsets import formset_factory

def response_from_purchase_form(testcase):
    
    main_form = PurchaseForm()
    item_forms = []
    
    for prefix, [model, form_name] in THINGS_WE_PURCHASE.items():
        PurchaseSubFormSet = formset_factory(form_name, extra=0)
        item_formset = PurchaseSubFormSet(prefix=prefix)
        item_forms.append((item_formset, model))

    pass
            