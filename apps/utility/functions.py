from Crypto.Cipher import AES
import base64

import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

def get_models_from_string(string):
    '''
    Takes a comma separated string of app and model names, returns Model objects.
    '''
    criteria_list = string.split(',') #Split along commas to get list of models

    models = []
    
    for model_string in criteria_list:
        
        app_name = model_string.split('.')[0]
        model_info = model_string.split('.')[1]
        model_name = model_info.split('__')[0]
        
        #The list of properties will be separated by a double underscore; the models from one another with an ampersand
        try:
            properties = model_info.split('__')[1].split('&')
        except IndexError:
            #In this case, we didn't find anything after the double underscore, so there ain't no properties.
            #We'll default to 'name,' which lots of models have.
            properties = ['name']

        model = ContentType.objects.get(app_label=app_name, model=model_name).model_class()
        models.append([model, properties])
    
    return models

def get_object_from_string(string):
        result_app = string.split('__')[0] #Now just app and model.
        result_model = string.split('__')[1] #....and the ID of the object.
        result_id = string.split('__')[2] #....and the ID of the object.
        
        #Get model of object in question
        model = ContentType.objects.get(app_label = result_app, model = result_model).model_class()
            
        #POSITIVE IDENTIFICATION CONFIRMED.  PROCEED WITH EXPERIMENT.
        result_object = model.objects.get(id=result_id)
        
        return result_object

def quick_search(search_phrase, model, field_names):
    '''
    Takes a search phrase, model instance, and field name and searches, returning a queryset.
    '''
    
    #This is some in-fucking-credible code right here.
    #I got this from: http://stackoverflow.com/questions/1227091/how-to-dynamically-provide-lookup-field-name-in-django-query
    #Of course, I added my own comments after grokking it.
    Qr = None #This is the Q object that we'll explode to use in the filter function.
    for field in field_names: #But first, we'll iterate through the field names and add them in order.
        #TODO: Make this go with haystack for bigger searches!
        q = Q(**{"%s__icontains" % str(field): str(search_phrase) })  #With the key 'name__icontains', set the value to "Ralph the Wonder Llama"
        if Qr:
            Qr = Qr | q # or & for filtering
        else:
            Qr = q
    result = model.objects.filter(Qr) #Now we expand the Q object we just created
    return result #since we used .filter(), the result will be a queryset

'''
Encryption Stuff
'''

'''
All AES blocks must be a multiple of 16 in length.
'''
block_size = 16


def pad_for_aes(data):
    '''
    Pad a string to prepare it for encryption
    '''
    candidate = str(data)
    length = len(candidate)

    missing = (block_size - length % block_size) #How many characters do we need to add?
    ascii_code = chr(block_size - length % block_size) #Get the appropriate ascii character
    padded_data = candidate + missing * ascii_code #Add that many of them 
    return padded_data

def unpad_for_aes(data):
    '''
    Unpad a string after decryption
    '''
    end = data[-1]
    int_from_ascii = ord(end)
    return data[0: - int_from_ascii]


def encrypt_string(data, key):
    '''
    Encrypt a string with AES.
    '''
    cipher = AES.new(key, AES.MODE_CBC)
    padded = pad_for_aes(data)
    encoded = base64.urlsafe_b64encode(cipher.encrypt(padded))    
    return encoded

def decrypt_string(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    
    decoded = cipher.decrypt(base64.urlsafe_b64decode(data.encode('ascii')))
    unpadded = unpad_for_aes(decoded)
    return unpadded


def get_daily_salt():    
    today = datetime.date.today()
    blah = "f9dj($*[wiiWD&FO$*Fife" #BLAAGH! CRAZY STRING FROM MASHING
    salt = blah[0:today.day] + str(today) + blah[today.day:] #Vary the salt by day.
    return salt

def daily_crypt(data, decrypt=False):
    key = get_daily_salt()
    
    if decrypt: #Are we asking it to decrypt?
        result = decrypt_string(data, key) #Yep, run the decrypt functino
    else:
        result = encrypt_string(data, key) #No, we want encryption
    return result