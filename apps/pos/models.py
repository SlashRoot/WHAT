from django.db import models

from products.models import BeverageInstance

from commerce.models import Exchange 

from hwtrack.models import Computer


import os

class PointOfSale(Computer):
    has_cash_drawer = models.BooleanField()
    
    def kick(self):
        if self.has_cash_drawer: #If everything goes well, this will return a 0.
            return os.system("ssh -i /home/slashroot_poke/.ssh/id_rsa catapult@" + self.ip_address + ''' "cmd /c 'type c:\kick.bat>COM3'" ''')
        else: #We don't have a cash drawer.  We can't comply.
            return True
    
    class Meta:
        verbose_name_plural = "Points of Sale"
        
        
class TemporarySaleModel(models.Model):
    item = models.CharField(max_length=65)
    size = models.CharField(max_length= 7, choices = [('small','small'), ('medium','medium'), ('large', 'large')])
    milk = models.CharField(max_length=25)
    price = models.DecimalField(max_digits= 7, decimal_places=2)
    taxable = models.BooleanField()