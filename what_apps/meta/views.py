from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from what_apps.meta.models import StatusLog
import socket

@csrf_exempt
def remote_heartbeat_success(request):
    #If this request isn't coming from the SlashRoot remote, we're going to raise a 403.
    if not socket.gethostbyname('remote.slashrootcafe.com') == request.META['REMOTE_ADDR']:
        return HttpResponseForbidden()
    
    StatusLog.objects.create(status=0)
    
    return HttpResponse(True)
    
    
    