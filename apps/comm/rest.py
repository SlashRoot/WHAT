from comm.services import SLASHROOT_TWILIO_ACCOUNT
from private import resources

class PhoneProviderRESTObject(object):
    def __init__(self, provider_object):
        self.provider = provider_object
        
    def place_new_call(self, from_number, to_number):
         if self.provider == "Tropo":
             response = requests.post('https://api.tropo.com/1.0/sessions/', 
                      data={
                            'token':'0aaea1598824a846a340ea4b597fc9672cfa5734fc4a2edcf8c2de5101277f765ec7e8743d379495f7969bc7', 
                            'toNumber':call_to_phone.remove_dashes(), 
                            'fromNumber':call_from_phone.remove_dashes(),
                            })
             session_id = urlparse.parse_qs(response.content)['id'][0].rstrip()
             return session_id

         if self.provider == "Twilio":
             ## THis is wet and ugly like your mom
             response = SLASHROOT_TWILIO_ACCOUNT.calls.create(to=to_number.number, from_=resources.SLASHROOT_MAIN_LINE, url="%s/comm/pickup_connect_auto/%s/%s/" % (resources.COMM_DOMAIN, _number.id))
             print response
        