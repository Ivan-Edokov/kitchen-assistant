from django.contrib import admin

from .models import RecipeIngredients, Recipe, Tag


class RecipeIngredientsInstanceInline(admin.TabularInline):
    model = RecipeIngredients


class RecipeTagsInstanceInline(admin.TabularInline):
    model = Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'text')
    inlines = (RecipeIngredientsInstanceInline,)
    tag = (RecipeTagsInstanceInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'color')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
