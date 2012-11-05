from django.contrib.auth.models import User
import sys

from django.core.management.base import BaseCommand


#The idea is to run this from the command line in this fashion:
#python manage.py bubblesizes 150 300 20 > static/css/bubble_locations.css
#The three arguments are 1) inner menu radius 2) outer menu radius 3) maximum number of bubbles


#Payload is potentially more complex than meets the eye.

class Command(BaseCommand):
 
    def handle(self, *args, **options):
 
        inner_radius=float(args[0])
        outer_radius=float(args[1])
        num_bubs=int(args[2])
 
        import math
        
        #degrees separating each bubble
        
        for outer_num in range(num_bubs):
        
            if outer_num == 0:
                continue
        
            degrees = float( float(360) / float(outer_num) )
               
            
            
            
            for num in range(outer_num):
                z = float(num)
                n = float( degrees * z)               
                
#                print '*****************************'
#                print 'outer_num is ' + str(outer_num)
#                print "this time the bubble number is " + str(z) + " and degrees is " + str(degrees)
#                print "so this bubble gets this many degrees: " + str(n)
#                print '*****************************'
                
                
                x_offset = inner_radius
                y_offset = inner_radius
                inner_x = (x_offset + inner_radius * math.cos( n * math.pi/180) ) 
                inner_y = (y_offset + inner_radius * math.sin( n * math.pi/180) ) 
                
                x_offset = inner_radius
                y_offset = inner_radius
                outer_x = (x_offset + outer_radius * math.cos( n * math.pi/180) ) 
                outer_y = (y_offset + outer_radius * math.sin( n * math.pi/180) ) 
                            
                print ".inner.bubble_" + str(num+1) + ".siblings_" + str(outer_num) + " {"
                print "margin-left:" + str(inner_x) + "px;"
                print "margin-top:" + str(inner_y) + "px;"
                print "}\n"
                
                print ".outer.bubble_" + str(num+1) + ".siblings_" + str(outer_num) + " {"
                print "margin-left:" + str(outer_x) + "px;"
                print "margin-top:" + str(outer_y) + "px;"
                print "}\n"
        
        