import csv
import os

from dotenv import load_dotenv

# import django.db.utils
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


load_dotenv()

USER = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):

        self.csvform(
            'data/tags.csv',
            Tag,
            ['name', 'color', 'slug'],
        )
        self.csvform(
            'data/ingredients.csv',
            Ingredient,
            ['name', 'measurement_unit'],
        )

        try:
            USER.objects.create_superuser(
                os.getenv('ADMIN_LOGIN', default=None),
                os.getenv('ADMIN_EMAIL', default=None),
                os.getenv('ADMIN_PAS', default=None),
            )
        except Exception:
            pass

    def csvform(self, file, model, head):
        with open(file, 'r', encoding='utf-8') as csvfile:
            freader = csv.DictReader(csvfile, fieldnames=head)
            for row in freader:
                try:
                    data = {h: row[h] for h in head}
                    model.objects.get_or_create(**data)
                except Exception:
                    continue
