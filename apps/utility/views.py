from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse, HttpResponseServerError

from django.utils import simplejson as json
from django import forms

import itertools

from django.utils import simplejson
from django.utils.datastructures import MultiValueDictKeyError

from utility.functions import get_models_from_string, quick_search, get_object_from_string

from do.models import TaskPrototype #Ideally, instead of importing this here, we'll have an autocomplete class that lives in do.functions.

def submit_generic(request, app_name, object_type):

    Model=ContentType.objects.get(app_label=app_name, model=object_type.lower()).model_class()

    class GenericForm(forms.ModelForm):
        class Meta:
            model = Model
 
    form=GenericForm(request.POST)
    
    #Start populating a dict to return.
    response_dict = {'errors': []} #Start with an empty list of errors.
    
    if form.is_valid():
        form.save()
        response_dict['success'] = True
    
    else:
        response_dict['success'] = False        
        for error in form.errors:
            response_dict['errors'].append(error) #Append to the list only if there are errors, otherwise this will remain an empty list
    
    #Whether or not the form was valid, we'll return a json dict with the bool for success and a list of errors (which will obviously be blank if there are none)
    return HttpResponse(simplejson.dumps(response_dict))
    
    
def submit_generic_partial(request, object_type, object_id):
    try:
        model=ContentType.objects.get(model=object_type).model_class()
    except:
        model=ContentType.objects.get(model=object_type.lower()).model_class()
        
        
    object = model.objects.get(id=object_id)
    
    object.__dict__.update(request.POST)
    
    #Lots of objects have descriptions and then get a little fudgy with unicode.
    #TODO: Find a better way to do this.
    try:
        object.description = str(request.POST['description'])
    except MultiValueDictKeyError:
        pass
    
    object.save()
        
    return HttpResponse(1)
    
    #TODO: Turn this into a generic ajax form
    #One interesting challenge will be to determine if the user has security to submit the form in question
    #ie, let's say that the form rendered on the page (for an anon) is some LowLevel form that anons are allowed to submit.
    #However, if the anon changes the flag to the name of a HighLevel form, we'll then need to check to make sure they are cool
    #We could modify the save methods by permission and that will clear the whole thing up.  That will take some discipline!
    
    #Example:
    #def submitGenericAjax(request):
    #    form_type=SomeMethodForDeterminingTheNameOfTheForm(request.POST['form_type'])
    #    
    #    if not user.has_perm_to_handle_form_type(form_type):
    #        raise a 403
    #
    #    form=form_type(request.POST)
    #    
    #    
    #    #....and so on

def autocomplete_dispatcher(request):
    return admin_autocomplete(request)
    
    '''
    Dubious and deprecated code to follow.
    TODO: Make this more generic and find it a good home.
    This is potential useful code for getting more than simply the name of the object to be autocompleted against.
    
    
    with_description = request.GET['with_description'] #1 or 0 depending on whether or not we need this autocomplete to return the description.  We're trusting that nobody is going to use this on a model that lacks a description field.

    if request.GET['lookup_type'] == "task_family":
        #We want to get the entire task family, including the progeny of the task.
        search_phrase=request.GET['term']  #What is our search phrase?    
        
        #We don't need to think about models here, we know we're dealing with TaskPrototype.
        task_prototypes = TaskPrototype.objects.filter(name__icontains = search_phrase)
        
        products = []
        
        for tp in task_prototypes: #Iterate through the potential parents
            label = str(tp.name) 
            
            result_meta = str(tp._meta) #Get the app and model for the result, ie auth.user
            result_id = str(tp.id) #Get the ID for the result.
            elephant = result_meta + "_" + result_id #Now we have "auth.user_34" or something
            
            tp_children_dict = {} #Start an empty dict for this TaskPrototype's children
            
            for progeny in tp.children.all(): #Iterate through the progeny objects for this TaskPrototype's children
                tp_children_dict[progeny.child.id] = progeny.child.name #With the child's ID as the key, set it's name to the value
                           
            product_dict = dict(elephant = elephant, label = label, xhr = label, children = tp_children_dict)    
            products.append(product_dict)       
            
        return HttpResponse(json.dumps(products))
    '''
    
        

def autocomplete_with_description(request):
    '''
    autocompletes for a model that has a description field and returns the name, description, and ID.
    '''
    search_phrase=request.GET['term']  #What is our search phrase?    
    models = get_models_from_string(request.GET['criterion'])    
    
    query = itertools.chain()
    
    for model in models:    
        search = quick_search(search_phrase, model, 'name') #TODO: How will we go about un-hardcoding name?
        query = itertools.chain(query, search)
    
        products = []
    
    for result in query:
        label = str(result) #TODO: Again, bad.
        
        result_meta = str(result._meta) #Get the app and model for the result, ie auth.user
        result_id = str(result.id) #Get the ID for the result.
        elephant = result_meta + "_" + result_id #Now we have "auth.user_34" or something
        
        try:
            description = result.description
        except AttributeError:
            description = "This model doesn't have a description."
            
                       
        product_dict = dict(elephant = elephant, label = label, xhr = label, description=description)    
        products.append(product_dict)       
        
    return HttpResponse(json.dumps(products))
    

def admin_autocomplete(request):
    search_phrase=request.GET['term']  #What is our search phrase?
    
    models = get_models_from_string(request.GET['criterion'])
    
    query = itertools.chain()
    
    for model, property_list in models:
        #Each item in models will be a list where the first item is a model, the second a list of field names in that model against which we'll search.    
        search = quick_search(search_phrase, model, property_list) #TODO: How will we go about un-hardcoding name?
        query = itertools.chain(query, search)
                
#        try:
#            fields = []
#            fields.append(model_info.split('__')[1])
#            for field in fields:
#                kwargs = {'%s__%s' % (field, 'ngram'): search_phrase}
#                search = SearchQuerySet().filter(**kwargs).models(model)
#                query = itertools.chain(query, search)
#        except IndexError:
        #TODO: Goodness, this is dreadful.  We need to be able to autocomplete against things besides 'name'
        #search = model.objects.filter(name__icontains = search_phrase)
        #Make the searches iterable
        

    products = []
    
    for result in query:
        label = str(result) #TODO: Again, bad.
        
        result_meta = str(result._meta) #Get the app and model for the result, ie auth.user
        result_id = str(result.id) #Get the ID for the result.
        elephant = result_meta + "_" + result_id #Now we have "auth.user_34" or something
                       
        product_dict = dict(elephant = elephant, label = label, xhr = label)    
        products.append(product_dict)       
        
    return HttpResponse(json.dumps(products))


def save_tags_for_object(request, model_info):
    '''
    Tags model app name, mdoel name, and ID, and saves tags from a django-taggit formatted tag string.
    '''
    #We can probably seperate this out into its own function
    object = get_object_from_string(model_info)
    object.tags.set(request.POST['tags'])
    
    return HttpResponse(1)