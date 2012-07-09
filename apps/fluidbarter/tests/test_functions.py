from fluidbarter.forms import PurchaseForm, THINGS_WE_PURCHASE
from django.forms.formsets import formset_factory
from utility.tests.factories import GroupFactory, UserFactory
from people.models import Group, GenericParty

def response_from_purchase_form(testcase):
    '''
    Dehydration function for basic purchase requests.
    
    Takes a TestCase with the follows attrs:
    
    buyer_user
    buyer_password
    buyer_name (can be a group or username)
    purchase_form_dict
    
    Returns a Response object obtained by logging in as buyer_user and posting purchase_form_dict to the purchase view.
    '''
    testcase.client.login(username=testcase.buyer_user.username, password=testcase.buyer_password)
    response = testcase.client.post('/commerce/record_purchase/%s/' % testcase.buyer_name, testcase.purchase_form_dict, follow=True)
    return response


def get_buyer_and_seller(testcase):
    '''
    Adds seller, buyer, and a few other attrs to testcase.
    '''
    testcase.buyer_password = "password"
    testcase.buyer_user = UserFactory.create(password=testcase.buyer_password)
    testcase.buyer_name = 'slashRoot'  # TODO: use buyer group name instead
    testcase.buyer_group = Group.objects.create(name="test_buyer_group")
    
    testcase.buyer = GenericParty.objects.get(user=testcase.buyer_user)
    testcase.seller = GroupFactory.create(name="test_group")
    


def get_main_and_item_forms(main_form_data=None, item_form_data=None):
    
    main_form = PurchaseForm(main_form_data)
    item_forms = []
    
    for prefix, [model, form_name] in THINGS_WE_PURCHASE.items():
        PurchaseSubFormSet = formset_factory(form_name, extra=0)
        item_formset = PurchaseSubFormSet(item_form_data, prefix=prefix)
        item_forms.append((item_formset, model))

    

    return main_form, item_forms
            