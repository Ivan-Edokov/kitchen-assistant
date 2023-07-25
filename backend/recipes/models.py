from django.db import models

from ingredients.models import Ingredient
from users.models import User

from . validators import validator_not_zero


class Recipe(models.Model):
    name = models.CharField(
        'Имя рецепта',
        max_length=200,
        null=False,
        blank=False,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        blank=False,
        null=False,
    )
    text = models.TextField(
        'Описание рецепта',
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        blank=False,
        null=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='recipe',
        verbose_name='Ингридиенты',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        verbose_name='Руцепт',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Колличество ингредиента',
        blank=False,
        null=False,
        validators=(validator_not_zero,),
    )
