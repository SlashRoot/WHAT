import struct, sys, getpass, os
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

from models import X10Module, X10ModuleCategory
import twilio 
from django.contrib.auth.decorators import login_required

@csrf_exempt
def change(request):
    command = request.POST['command']
    module_id = request.POST['module_id']
    module = X10Module.objects.get(id=module_id)
    os.system('ssh -i /home/power/.ssh/id_rsa power@10.0.0.127 -o StrictHostKeyChecking=no "heyu ' + command + ' %s"' % (module.housecode))
    return HttpResponse('llamas')

@login_required
def switch(request):
    modules = X10Module.objects.all()
    return render(request, 'power/switch.html', locals() )