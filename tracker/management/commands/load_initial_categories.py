from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.features.category.models import GroceryCategory

class Command(BaseCommand):
    help = 'Load initial grocery categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                "name": "Fruits & Vegetables",
                "description": "Fresh fruits and vegetables"
            },
            {
                "name": "Dairy & Eggs",
                "description": "Milk, cheese, yogurt, and eggs"
            },
            {
                "name": "Pantry",
                "description": "Rice, flour, pasta, and other staples"
            },
            {
                "name": "Snacks",
                "description": "Chips, cookies, and other snack items"
            },
            {
                "name": "Beverages",
                "description": "Drinks, juices, and beverages"
            },
            {
                "name": "Meat & Seafood",
                "description": "Fresh and frozen meat and seafood"
            },
            {
                "name": "Household",
                "description": "Cleaning supplies and household items"
            },
            {
                "name": "Other",
                "description": "Other items"
            }
        ]

        for category_data in categories:
            category, created = GroceryCategory.objects.get_or_create(
                name=category_data["name"],
                defaults={
                    "description": category_data["description"],
                    "created_at": timezone.now(),
                    "updated_at": timezone.now()
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created category "{category.name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category "{category.name}" already exists')
                ) 