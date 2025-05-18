from rest_framework import serializers
from .models import Budget

class BudgetSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    currency_symbol = serializers.CharField(read_only=True)

    class Meta:
        model = Budget
        fields = ('id', 'user', 'amount', 'period', 'currency', 'currency_symbol',
                 'notification_threshold', 'notification_sent', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'notification_sent')

class BudgetAnalyticsSerializer(serializers.Serializer):
    budget_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    period = serializers.CharField()
    currency = serializers.CharField()
    currency_symbol = serializers.CharField()
    notification_threshold = serializers.DecimalField(max_digits=10, decimal_places=2)
    notification_sent = serializers.BooleanField()
    category_breakdown = serializers.ListField(child=serializers.DictField()) 