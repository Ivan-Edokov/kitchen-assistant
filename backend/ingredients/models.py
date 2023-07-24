from django.db import models


class Ingredient(models.Model):

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        null=False,
        blank=False,
    )

    measurement_unit = models.CharField(
        'Еденица измерения колличества ингридиента',
        max_length=200,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit',
            )
        ]

    def __str__(self):
        return self.name
