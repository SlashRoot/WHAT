from django.db import models
from what_apps.hwtrack.models import Device

"""
Here we assume the existence of a model called Device.
You'll need to edit the line below to reflect the ap in which you define Device.

Ours looks like this:

class Device(models.Model):
    name=models.CharField(max_length=60)
    make=models.CharField(max_length=200, null=True, blank=True)
    model=models.CharField(max_length=200, null=True, blank=True)
    description=models.TextField()
    owner=models.ForeignKey(User)
    purpose=models.ManyToManyField(Purpose, through='PurposeRationale')
    location=models.IntegerField(choices=LOCATIONS)
    quick_id=models.CharField(max_length=30, null=True, blank=True)
    
    def __unicode__(self):
        return self.name + " at " + self.get_location_display()
"""


class X10ModuleCategory(models.Model):
    name=models.CharField(max_length=60)
    description=models.TextField()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "X10ModuleCategories"


class X10Module(models.Model):
    make=models.CharField(max_length=200, null=True, blank=True)
    model=models.CharField(max_length=200, null=True, blank=True)
    dimmable = models.BooleanField()
    housecode = models.CharField(max_length=3)
    device = models.OneToOneField(Device)
    category = models.ForeignKey(X10ModuleCategory, related_name="modules")
    
    def __unicode__(self):
        return self.housecode + " (" + self.device.model.name + ")"

