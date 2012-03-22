from django.shortcuts import render
from do.models import Task
 
def animal_shipping(request):
    '''
    Provides users with the option of ordering animals.
    '''
    ship = request.POST["destination"]
    if ship == "Narobi":
        return render(request,"map_of_Nirobi")
    else: 
        return render(request,"map_of_africa")
    
    

def sandbox(request):
    t  = Task.objects.get(id=18)
    return render(request, 'sandbox/sandbox.html', {'t': t})
    