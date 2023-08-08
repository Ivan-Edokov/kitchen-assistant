from colorfield.fields import ColorField
from django.db import models

from ingredients.models import Ingredient
from users.models import User
from .validators import validator_not_zero


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
        blank=False,
        null=False,
    )
    color = ColorField(
        verbose_name='Цвет',
        unique=True,
        null=True,
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=200,
        null=True,
        blank=False,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} [{self.color}]'


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
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    favorite = models.ManyToManyField(
        User,
        verbose_name='Избранное',
        related_name='favorite_recipes',
        blank=True,
    )
    shopping_card = models.ManyToManyField(
        User,
        verbose_name='В карточку покупок',
        related_name='shopping_recipes',
        blank=True,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name

    @property
    def favorite_count(self):
        return self.favorite.count()


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        verbose_name='Ингридиенты',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Руцепт',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Колличество ингредиента',
        blank=False,
        null=False,
        validators=(validator_not_zero,),
    )
