import openai
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Avg, Max
from datetime import timedelta
import json

from .models import GroceryItem, ShoppingList, ShoppingListItem, Budget

class SmartShoppingListGenerator:
    def __init__(self, user):
        self.user = user
        openai.api_key = settings.OPENAI_API_KEY

    def _get_purchase_history(self, days=90):
        """Get user's purchase history for analysis"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get frequently bought items
        frequent_items = GroceryItem.objects.filter(
            user=self.user,
            created_at__range=(start_date, end_date)
        ).values(
            'name', 'category__name', 'unit'
        ).annotate(
            purchase_count=Count('id'),
            avg_quantity=Avg('quantity'),
            avg_price=Avg('price'),
            last_purchased=Max('created_at')
        ).order_by('-purchase_count')

        return list(frequent_items)

    def _get_budget_info(self):
        """Get user's current budget information"""
        try:
            budget = Budget.objects.filter(user=self.user).latest('created_at')
            return {
                'amount': float(budget.amount),
                'currency': budget.currency,
                'period': budget.period,
                'currency_symbol': budget.currency_symbol
            }
        except Budget.DoesNotExist:
            return None

    def generate_list(self, name=None):
        """Generate a smart shopping list based on user's history and preferences"""
        purchase_history = self._get_purchase_history()
        budget_info = self._get_budget_info()

        # Prepare the prompt for OpenAI
        prompt = {
            "role": "system",
            "content": """You are a smart shopping assistant that helps users create optimized grocery lists. 
            Analyze the purchase history and create a suggested shopping list that:
            1. Includes frequently bought items that might need replenishment
            2. Suggests quantities based on past purchase patterns
            3. Estimates prices based on past purchases
            4. Prioritizes items based on purchase frequency and last purchase date
            5. Groups items by category
            6. Stays within budget constraints
            7. Includes brief notes about why each item is suggested

            Return the response in this exact JSON format:
            {
                "list_name": "suggested name based on current month/season",
                "items": [
                    {
                        "name": "item name",
                        "category": "category name",
                        "quantity": numeric quantity,
                        "unit": "unit of measurement",
                        "estimated_price": numeric price,
                        "priority": "low/medium/high",
                        "notes": "reason for suggestion"
                    }
                ],
                "total_estimated_cost": numeric total,
                "suggestions": ["list of shopping tips based on analysis"]
            }"""
        }

        # Add user context
        prompt_content = {
            "role": "user",
            "content": f"""
            Purchase History (last 90 days): {json.dumps(purchase_history, default=str)}
            Budget Information: {json.dumps(budget_info) if budget_info else 'No budget set'}
            
            Please generate a smart shopping list based on this data.
            Consider:
            - Frequently bought items
            - Items that might need replenishment based on last purchase date
            - Seasonal items
            - Budget constraints
            - Shopping patterns
            """
        }

        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[prompt, prompt_content],
                temperature=0.7,
                max_tokens=2000
            )

            # Parse the response
            suggestion_data = json.loads(response.choices[0].message.content)

            # Create shopping list
            shopping_list = ShoppingList.objects.create(
                user=self.user,
                name=name or suggestion_data['list_name'],
                status='draft',
                notes="\n".join(suggestion_data.get('suggestions', []))
            )

            # Create shopping list items
            for item_data in suggestion_data['items']:
                ShoppingListItem.objects.create(
                    shopping_list=shopping_list,
                    name=item_data['name'],
                    category_id=self._get_or_create_category(item_data['category']),
                    quantity=item_data['quantity'],
                    unit=item_data['unit'],
                    estimated_price=item_data['estimated_price'],
                    priority=item_data['priority'],
                    notes=item_data['notes']
                )

            return shopping_list

        except Exception as e:
            raise Exception(f"Failed to generate shopping list: {str(e)}")

    def _get_or_create_category(self, category_name):
        """Get or create a category by name"""
        from .models import GroceryCategory
        category, _ = GroceryCategory.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Category for {category_name} items'}
        )
        return category.id 