# Generated by Django 4.2.3 on 2023-08-19 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_alter_ingredient_name_and_more'),
        ('recipes', '0009_alter_recipe_options_recipe_pub_date'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredients',
            new_name='RecipeIngredient',
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Рецепты Ингредиенты', 'verbose_name_plural': 'Рецепты Ингредиенты'},
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_recipe_ingredient'),
        ),
    ]