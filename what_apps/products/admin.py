from django.contrib import admin
from what_apps.utility.admin import autoregister

from models import Ingredient, IngredientStock


class IngredientStockAdmin(admin.ModelAdmin): 
    model = IngredientStock
    list_display = ('index', 'id', 'ingredient', 'created', 'depleted')

admin.site.register(Ingredient)
admin.site.register(IngredientStock, IngredientStockAdmin)

autoregister('products')