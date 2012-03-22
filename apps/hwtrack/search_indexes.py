from hwtrack.models import Device, QuickId, DeviceModel
from haystack.indexes import RealTimeSearchIndex, CharField, DateTimeField, EdgeNgramField, IntegerField
from haystack import site

class DeviceIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    quick = CharField(null=True)
    short = CharField()
    
    def prepare_quick(self, obj):
        try:
            return self.quick
        except:
            return None 
    
    def prepare_short(self, obj):
        try:
            return obj.quick.id + " - " + obj.model.brand.name + " " + obj.model.designation
        except QuickId.DoesNotExist:
            return obj.model.brand.name + " " + obj.model.designation
        except DeviceModel.DoesNotExist:
            return obj.__unicode__()
    
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Device.objects.all()
    
class DeviceModelIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    quick = CharField(null=True)
    short = CharField()
    autocomplete_index = EdgeNgramField(use_template=True)
    
    def prepare_short(self, obj):
        return obj.name
    
    def get_queryset(self):
        return DeviceModel.objects.all()
    
site.register(Device, DeviceIndex)
site.register(DeviceModel, DeviceModelIndex)
