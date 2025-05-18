from rest_framework import serializers
from .models import Receipt, GroceryItem

class ReceiptSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = serializers.ImageField(required=True, write_only=False)
    
    class Meta:
        model = Receipt
        fields = ('id', 'user', 'image', 'platform', 'status', 'processed_text',
                 'processed_data', 'total_amount', 'created_at', 'updated_at')
        read_only_fields = ('status', 'processed_text', 'processed_data', 'total_amount',
                          'created_at', 'updated_at')
        extra_kwargs = {
            'platform': {
                'required': True,
                'help_text': 'Name of the platform (e.g., Zepto, Blinkit)'
            },
            'image': {
                'help_text': 'Receipt image file (JPEG, PNG format)',
                'required': True
            }
        }

class GroceryItemSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = GroceryItem
        fields = ('id', 'user', 'name', 'category', 'category_name', 'price',
                 'quantity', 'unit', 'platform', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at') 