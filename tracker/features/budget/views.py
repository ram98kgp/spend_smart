from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema

from .models import Budget
from .serializers import BudgetSerializer, BudgetAnalyticsSerializer
from .utils import send_budget_notification
from ..receipt.models import GroceryItem

class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing budgets and viewing analytics.
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns budgets for the current user.
        """
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get budget analytics for both weekly and monthly periods",
        responses={
            200: BudgetAnalyticsSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get budget analytics for both weekly and monthly periods."""
        today = timezone.now().date()
        
        # Get both weekly and monthly budgets for the user
        weekly_budget = self.get_queryset().filter(period='weekly').order_by('-created_at').first()
        monthly_budget = self.get_queryset().filter(period='monthly').order_by('-created_at').first()

        if not weekly_budget and not monthly_budget:
            return Response({
                'error': 'No budgets found. Please set at least one budget first.'
            }, status=status.HTTP_404_NOT_FOUND)

        def get_period_analytics(budget, start_date):
            if not budget:
                return None

            # Calculate total spent amount for the period
            spent = GroceryItem.objects.filter(
                user=request.user,
                created_at__date__gte=start_date,
                created_at__date__lte=today
            ).aggregate(total=Sum('price'))['total'] or Decimal('0')

            # Check if we need to send a notification
            if budget.should_send_notification(spent):
                try:
                    send_budget_notification(request.user, budget, spent)
                    budget.notification_sent = True
                    budget.save()
                except Exception as e:
                    print(f"Failed to send budget notification: {e}")

            # Get spending by category for the period
            category_spending = GroceryItem.objects.filter(
                user=request.user,
                created_at__date__gte=start_date,
                created_at__date__lte=today
            ).values('category__name').annotate(
                total=Sum('price')
            ).order_by('-total')

            remaining = budget.amount - spent

            return {
                'period': budget.period,
                'budget_amount': budget.amount,
                'spent_amount': spent,
                'remaining_amount': remaining,
                'notification_threshold': budget.notification_threshold,
                'notification_sent': budget.notification_sent,
                'start_date': start_date,
                'end_date': today,
                'category_breakdown': [
                    {
                        'category_name': item['category__name'],
                        'spent_amount': item['total'],
                        'percentage_of_total': (item['total'] / spent * 100) if spent > 0 else Decimal('0')
                    } for item in category_spending
                ]
            }

        # Calculate start dates for both periods
        weekly_start = today - timedelta(days=today.weekday()) if weekly_budget else None
        monthly_start = today.replace(day=1) if monthly_budget else None

        # Get analytics for both periods
        weekly_analytics = get_period_analytics(weekly_budget, weekly_start) if weekly_budget else None
        monthly_analytics = get_period_analytics(monthly_budget, monthly_start) if monthly_budget else None

        response_data = {
            'weekly': weekly_analytics,
            'monthly': monthly_analytics
        }

        return Response(response_data) 