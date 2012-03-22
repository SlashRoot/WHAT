from django.contrib import admin
from utility.admin import autoregister

from models import Ingredient, IngredientStock


class IngredientStockAdmin(admin.ModelAdmin): 
    model = IngredientStock
    list_display = ('index', 'id', 'ingredient', 'created', 'depleted')

admin.site.register(Ingredient)
admin.site.register(IngredientStock, IngredientStockAdmin)

autoregister('products')