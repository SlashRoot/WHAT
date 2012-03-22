import datetime
from haystack.indexes import RealTimeSearchIndex, CharField, DateTimeField, EdgeNgramField
from haystack import site

from models import ProductBrand, Ingredient, IngredientProperty

class ProductBrandIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    autocomplete_index = EdgeNgramField(use_template=True)
    short = CharField()
    
    def prepare_short(self, obj):
        return obj.name

site.register(ProductBrand, ProductBrandIndex)

class IngredientIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True, template_name="search/indexes/generic_name_index.html")
    autocomplete_index = EdgeNgramField(use_template=True, template_name="search/indexes/generic_name_index.html")
    short = CharField()
    
    def prepare_short(self, obj):
        return obj.name

site.register(Ingredient, IngredientIndex)
site.register(IngredientProperty, IngredientIndex)                