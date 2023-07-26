# Generated by Django 4.2.3 on 2023-07-25 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_alter_ingredient_name_and_more'),
        ('recipes', '0002_recipeingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipeingredients',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='recipeingredients',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='ingredients.ingredient', verbose_name='Ингридиенты'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Руцепт'),
        ),
    ]