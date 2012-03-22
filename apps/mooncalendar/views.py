# Create your views here.
from django.template import Context, loader
from django.http import HttpResponse
from mooncalendar.models import Event, Moon, Day24
import datetime
from django.shortcuts import render_to_response as render


def index(request, moon_name):
    unslugified_moon_name = moon_name.replace('-', " ")
    this_moon=Moon.objects.get(name__icontains = unslugified_moon_name)
    
    moon_list = Moon.objects.all()
    
    new_moon_date=this_moon.new
    ddelta = datetime.timedelta( 10 )
    next_moon_date=Moon.objects.get(new__range = [ this_moon.waning, this_moon.waning + ddelta ] )
    days_between=next_moon_date.new-new_moon_date    
    
    days_covered=[Day24(date=new_moon_date+datetime.timedelta(days=p)) for p in range(days_between.days)]
    
    #Coloring
    
    #PHASES
    #0 = Waxing Crescent
    #1 = Waxing Gibbous
    #2 = Waning Gibbous
    #3 = Waning Crescent
    phase = 0
    days_since_new = 0
    
    background_gradient_speed = 18
    text_gradient_speed = 25
    
    for day in days_covered:
        
        #Waxing Crescent
        if phase == 0:
            color_int = 255 - (days_since_new * background_gradient_speed)
            color=str(color_int)
            
            #If we're in the first phase of the moon, the text is still black
            text_color=str(0)
        
        #Waxing Gibbous   
        if phase == 1:
            color_int = 255 - (days_since_new * background_gradient_speed)
            color=str(color_int)
            
            #Now we'll start with the colors.
            text_color_int = days_since_new * text_gradient_speed
            text_color=str(text_color_int)
            
        if day.date.day == this_moon.waxing.day:
            phase = 1
            day.special="First Quarter"
        
        
        #Waning Gibbous
        if phase == 2:
            color_int = ( (days_since_new-14) * background_gradient_speed)
            color=str(color_int)
            
            text_color_int = 255 - ( (days_since_new-20) * text_gradient_speed)
            text_color=str(text_color_int)
            
        if day.date.day == this_moon.full.day:
            color=str(0)
            text_color = str(255)
            day.special="Full Moon"
            
            phase = 2
            
            
        #Waning Crescent        
        if phase == 3:
            color_int = ( (days_since_new-14) * background_gradient_speed)
            color=str(color_int)
            
            #If we're in the last phase of the moon, the text is also black
            text_color=str(0)
        
        if day.date.day == this_moon.waning.day:
            text_color=str(0)
            phase = 3
            day.special="Third Quarter"
        
        
        days_since_new += 1
        day.color = 'rgb(' + color +',' + color + ',' + color +')'
        day.text_color = 'rgb(' + text_color +',' + text_color + ',' + text_color +')'
        
        
        
    
    #event_list = Event.objects.filter(event_date__range=(new_moon_date, next_moon_date))
    event_list = Event.objects.filter(event_date__range = [new_moon_date, next_moon_date.new])
    day_after_new=new_moon_date+datetime.timedelta(1)
    
    t = loader.get_template('mooncalendar/mooncycle')
     #   'event_list': event_list,    
    next_moon_date=next_moon_date.new
    days_between=days_between.days
    days_covered=days_covered
    return render('mooncalendar/mooncycle', locals())

def moons_info(request):
    moons = Moon.objects.all()
    return render('mooncalendar/moons_info.html', locals())
