from rest_framework import serializers
from .models import GroceryCategory

class GroceryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryCategory
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at') 