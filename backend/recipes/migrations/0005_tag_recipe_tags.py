# Generated by Django 4.2.3 on 2023-07-26 15:12

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipeingredients_ingredient'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название тега')),
                ('color', colorfield.fields.ColorField(blank=True, default=None, image_field=None, max_length=18, null=True, samples=None, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=200, null=True, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.tag', verbose_name='Теги'),
        ),
    ]