from comm.service import SLASHROOT_TWILIO_ACCOUNT
from private import API_Tokens, resources

class PhoneProviderRESTObject(object):
    def __init__(self, provider_object):
        self.provider = provider_object
        
    def place_new_call(self, from_number, to_number):
         if provider.name == "Tropo":
             response = requests.post('https://api.tropo.com/1.0/sessions/', 
                      data={
                            'token':'0aaea1598824a846a340ea4b597fc9672cfa5734fc4a2edcf8c2de5101277f765ec7e8743d379495f7969bc7', 
                            'toNumber':call_to_phone.remove_dashes(), 
                            'fromNumber':call_from_phone.remove_dashes(),
                            }
             )

         if provider.name == "Twilio":
             response = SLASHROOT_TWILIO_ACCOUNT.calls.create(to=number_object.number, from_=resources.SLASHROOT_MAIN_LINE, url="%s/comm/pickup_connect_auto/%s/%s/" % (resources.COMM_DOMAIN, number, conference_id))
             
         session_id = urlparse.parse_qs(response.content)['id'][0].rstrip()
         return session_id