from django.core.management.base import BaseCommand
from do.models import TaskGenerator, RandomRecurringTaskGenerator, TaskAccessPrototype, TaskAccess
from mellon.models import Privilege

class Command(BaseCommand):
 
    def handle(self, *args, **options):
        '''
        Consider each taskgenerator; generate tasks accordingly
        '''
        
        #First let's handle Randomly Recurring Tasks
        
        #TODO: Adopt some convention for 'exempt' periods
        for generator in RandomRecurringTaskGenerator.objects.all():
            privilege = Privilege.objects.get(id=5) #TODO: Make generic so others than SlashRoot can use it
            task = generator.roll_the_dice(privilege)
            print task