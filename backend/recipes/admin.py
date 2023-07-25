from django.contrib import admin

from .models import RecipeIngredients, Recipe


class RecipeIngredientsInstanceInline(admin.TabularInline):
    model = RecipeIngredients


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'text')
    inlines = (RecipeIngredientsInstanceInline,)


admin.site.register(Recipe, RecipeAdmin)
