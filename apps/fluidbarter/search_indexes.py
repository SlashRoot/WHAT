from commerce.models import TradeElement

from haystack.indexes import RealTimeSearchIndex, CharField, DateTimeField, EdgeNgramField, IntegerField
from haystack import site

class TradeElementIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True, template_name="search/indexes/generic_name_index.html")
    quick = CharField(null=True)
    short = CharField()
    autocomplete_index = EdgeNgramField(use_template=True, template_name="search/indexes/generic_name_index.html")
    
    def prepare_short(self, obj):
        return obj.name
    
    def get_queryset(self):
        return TradeElement.objects.all()
    
site.register(TradeElement, TradeElementIndex)
