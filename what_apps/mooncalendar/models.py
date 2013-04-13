import datetime

from django.db import models
from django.template.defaultfilters import slugify


class Event(models.Model):
    '''
    DOMINICK
    '''
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    event_date = models.DateTimeField('event date')


#class MoonManager(models.Manager):
#    
#    #Moons need to be queried in the order they occur, not in the order they were entered.
#    def get_query_set(self):
#        return super(MoonManager, self).get_query_set().order_by('new')


class Moon(models.Model): #Let's define the model for a moon cycle.
    name = models.CharField(max_length=200, unique=True)
    new = models.DateTimeField()
    waxing = models.DateTimeField()
    full = models.DateTimeField()
    waning = models.DateTimeField()
    
    class Meta:
        ordering = ('new',)
    
    def __unicode__(self):
        return self.name + " " + unicode(self.new.year) + "-" + unicode(self.new.month)
    
    def get_absolute_url(self):
        return '/happenings/%s/' % slugify(self.name)
    
    
    '''
    For getting nearby moons, we know that the date between this moon's new moon date
    and nearby moons' waning and waxing dates will be within 9 days.
    We'll use that to our advantage.
    '''
    
    def previous_moon(self):
        ddelta = datetime.timedelta( 9 ) #9 days
        try:
            previous_moon = Moon.objects.get(waning__range = [ self.new - ddelta, self.new ] )
        except:
            pass #raise KnowledgeError - there should never be more or less than 1 moon whose waning date is 9 or so days from the next moon's New date
            raise
        return previous_moon
    
    def subsequent_moon(self):
        ddelta = datetime.timedelta( 9 )
        subsequent_moon=Moon.objects.get(new__range = [ self.waning, self.waning + ddelta ] )
        return subsequent_moon

    def date_falls_within(self, date):
        '''
        Returns a tuple: 
        1) A boolean of whether or not the date is within this moon
        2) if False, whether it's before or after
        '''
        #How long is the distance between the date in question and this new moon?
        #Will be negative is date is before, positive if it is after.
        diff = date - self.new
        
        #Is the date before or after?
        if not diff.days < 0: #Is this a positive number?
            if diff < self.length(): #Is the distance from the new moon less than the length of this moon?
                return True, None
            return False, 'after'  #This date is after this moon's length.  Thus AFTER this moon.
            
        else: #The date is before this moon's new date.  Thus BEFORE this moon.
            return False, 'before'
    
    
    
    def length(self):
        '''
        Returns a timedelta object of the length of this moon.
        '''
        subsequent_moon = self.subsequent_moon()
        time_between=subsequent_moon.new - self.new    
        
        #Not used for this method, but preserved for later use.
        #days_covered=[Day24(date=self.new + datetime.timedelta(days=p)) for p in range(days_between.days)]
        
        return time_between
    
    
    def length_waxing_crescent(self):
        return self.waxing - self.new
    
    def length_waxing_gibbous(self):
        return self.full - self.waxing
    
    def length_waning_crescent(self):
        return self.waning - self.full
        
    def length_waning_gibbous(self):
        try:
            return self.subsequent_moon().new - self.waning
        except Moon.DoesNotExist:
            return "Information about subsequent moon has not been entered."
    
    def length_waxing(self):
        return self.length_waxing_crescent() + self.length_waxing_gibbous()
    
    def length_waning(self):
        return self.length_waning_crescent() + self.length_waning_gibbous()
    
        
class Day24(models.Model):
    date = models.DateTimeField()
    color = models.CharField(max_length=25)
    text_color = models.CharField(max_length=25)


def get_moon_by_date(date):
    

    #First let's get all moons whose New date is in the same month as our date.
    #In some cases, such as July 2011, there are two new moons in the same month.
    #We want only the first such moon.
    nearby_moon = Moon.objects.filter(new__month = date.month, new__year = date.year)[0]

    #This will be a tuple - see the date_falls_within method.
    falls_within = nearby_moon.date_falls_within(date)
    
    
    if falls_within[0]: #If this date falls inside this moon, we have a winner!
        return nearby_moon
    
    '''
    If it's not within this moon, but in the same month as the new moon,
    then we know that if it's before the new moon, it's in the previous moon.
    If it's after this moon's coverage, it's in the subsequent moon.
    '''
    
    if falls_within[1] == 'before':
        return nearby_moon.previous_moon()
    
    if falls_within[1] == 'after':
        return nearby_moon.subsequent_moon()



    