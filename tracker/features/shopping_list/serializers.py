from rest_framework import serializers
from .models import ShoppingList, ShoppingListItem

class ShoppingListItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ShoppingListItem
        fields = ('id', 'name', 'category', 'category_name', 'quantity', 'unit',
                 'estimated_price', 'priority', 'is_purchased', 'purchase_frequency',
                 'last_purchase_date', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('purchase_frequency', 'last_purchase_date', 'created_at', 'updated_at')

class ShoppingListSerializer(serializers.ModelSerializer):
    items = ShoppingListItemSerializer(many=True, read_only=True)
    total_estimated_cost = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    completed_items = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'name', 'status', 'budget', 'notes',
                 'items', 'total_estimated_cost', 'total_items',
                 'completed_items', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def get_total_estimated_cost(self, obj):
        return sum(
            (item.estimated_price or 0) * item.quantity 
            for item in obj.items.all()
        )

    def get_total_items(self, obj):
        return obj.items.count()

    def get_completed_items(self, obj):
        return obj.items.filter(is_purchased=True).count() 