#HARDWARE_AQUISITION = BudgetLine.objects.get(id=3)

from django.db import models
from django.contrib.auth.models import User

import re

from django.utils.translation import ugettext_lazy as _
from django.forms import fields

from products.models import Product, ProductBrand
from commerce.models import RealThing

MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
mac_re = re.compile(MAC_RE)


class DisplayType(models.Model):
    name=models.CharField(max_length=20)

class DeviceInterface(models.Model):
    name=models.CharField(max_length=20)
    
class Purpose(models.Model):
    name=models.CharField(max_length=80)
    description=models.TextField()

class PrinterType(models.Model):
    name=models.CharField(max_length=20)

class PurposeRationale(models.Model):
    '''This model asks:
    Why is a device assigned to its current purpose(s)?
    '''
    name=models.CharField(max_length=80)
    #heres the additional description.
    description=models.TextField()
    device=models.ForeignKey('Device')
    purpose=models.ForeignKey('Purpose')
    
class DeviceModel(Product): #Ethereal
    '''
    The make and model of a device.
    IE, "Asus GTX9000" or whatever.
    This will be the "GTX9000" part.
    '''
    designation = models.CharField(max_length=80)
    brand=models.ForeignKey(ProductBrand)
    
    def __unicode__(self):
        return self.brand.name + " " + self.name

class QuickId(models.Model):
    '''
    Nothing but an int field.  Maybe some methods someday?
    '''
    id = models.CharField(max_length=10, primary_key=True)
    thing = models.OneToOneField('commerce.RealThing', related_name="quick")


class Device(RealThing): 
    model = models.ForeignKey(DeviceModel)
    purpose=models.ManyToManyField(Purpose, through='PurposeRationale', blank=True, null=True)
    location=models.ForeignKey('presence.Location', blank=True, null=True)

    def __unicode__(self):
        return self.model.name

class NetworkDevice(Device):
    ip_address=models.IPAddressField()
    mac_address=models.CharField(max_length=17, blank=True, null=True)
    lan_speed=models.IntegerField()
    hostname=models.CharField(max_length=60)
    inward_neighbour = models.ForeignKey('self', related_name="outward_neighbour", null=True, blank=True)
    connected=models.BooleanField()
    
    def list_outward_neighbors(self):
        return self.outward_neighbours.all()
    
    def incoming_budget_line(self):
        if not self.model.incoming_budget_line:
            self.model.incoming_budget_line = HARDWARE_AQUISITION
            
        return self.model.incoming_budget_line

class ComputerFormFactor(models.Model):
    name=models.CharField(max_length=30)        
    
class Computer(NetworkDevice):
    form_factor=models.ForeignKey(ComputerFormFactor)
    public_use=models.BooleanField()
    #we need to associate computers with components contained and peripherals attached
 
class WAP(NetworkDevice):
    SSID=models.CharField(max_length=100)
    #a,b,g, or n
    broadcast=models.CharField(max_length=10)

class Peripheral(Device):
    connectivity=models.ForeignKey(DeviceInterface)

class Printer(Peripheral):
    type=models.ForeignKey(PrinterType)
    multifunction=models.BooleanField()
        
class Display(Device):
    type=models.ForeignKey(DisplayType)

class Component(Device):
    connectivity=models.ManyToManyField(DeviceInterface)

class RAM(Component):
    #DDR, SDRAM, DRAM Etc.
    type=models.CharField(max_length=200)
    size=models.IntegerField() #should be followed with a unit of measurement
        
class HDD(Component):
    capacity=models.IntegerField() #should be followed with a unit of measurement

class PowerSupply(Component):
    max_output=models.IntegerField()
    power_connectivity=models.ForeignKey(DeviceInterface)
    
class PowerAdapter(Device):
    voltage=models.FloatField() 
    amperage=models.FloatField()
    
class CPU(Component):
    FQ=models.IntegerField()#Should be followed by GHZ or MHZ
    
class Cable(Device):
    connectivity=models.ManyToManyField(DeviceInterface)
     

class PowerStrip(Device):
    port_value=models.IntegerField()
    plug_form_factor=models.CharField(max_length=40)
    
    
    