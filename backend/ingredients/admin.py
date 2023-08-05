from django.contrib import admin

from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
