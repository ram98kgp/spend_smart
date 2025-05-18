# tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal

from .features.budget.models import Budget
from .features.receipt.models import GroceryItem
from .features.utils import send_budget_notification

# Get logger for this module
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def check_budget_thresholds(self):
    """
    Periodic task to check budget thresholds and send notifications
    """
    logger.info(f"Starting budget threshold check task (task_id: {self.request.id})")
    
    today = timezone.now().date()
    logger.info(f"Checking budgets for date: {today}")
    
    # Get all budgets where notification hasn't been sent yet
    budgets = Budget.objects.filter(notification_sent=False)
    budget_count = budgets.count()
    logger.info(f"Found {budget_count} budgets pending notification check")
    
    notifications_sent = 0
    errors = 0
    
    for budget in budgets:
        try:
            logger.info(f"Processing budget for user {budget.user.username} "
                       f"(user_id: {budget.user.id}, budget_id: {budget.id})")
            
            # Calculate period start date
            if budget.period == 'weekly':
                start_date = today - timedelta(days=today.weekday())
                logger.debug(f"Weekly budget: Start date calculated as {start_date}")
            else:  # monthly
                start_date = today.replace(day=1)
                logger.debug(f"Monthly budget: Start date calculated as {start_date}")
            
            # Calculate spent amount
            spent = GroceryItem.objects.filter(
                user=budget.user,
                created_at__date__gte=start_date,
                created_at__date__lte=today
            ).aggregate(total=Sum('price'))['total'] or Decimal('0')
            
            logger.info(f"User {budget.user.username} has spent {budget.currency_symbol}{spent} "
                       f"out of {budget.currency_symbol}{budget.amount} ({budget.period} budget)")
            
            # Check if notification should be sent
            if budget.should_send_notification(spent):
                logger.info(f"Threshold reached for user {budget.user.username}: "
                          f"Spent {budget.currency_symbol}{spent} >= "
                          f"Threshold {budget.currency_symbol}{budget.notification_threshold}")
                try:
                    send_budget_notification(budget.user, budget, spent)
                    budget.notification_sent = True
                    budget.save()
                    notifications_sent += 1
                    logger.info(f"Successfully sent notification to user {budget.user.username}")
                except Exception as e:
                    errors += 1
                    logger.error(f"Failed to send notification to user {budget.user.username}: {str(e)}", 
                               exc_info=True)
            else:
                logger.debug(f"No notification needed for user {budget.user.username}: "
                           f"Spent {budget.currency_symbol}{spent} < "
                           f"Threshold {budget.currency_symbol}{budget.notification_threshold}")
                
        except Exception as e:
            errors += 1
            logger.error(f"Error processing budget for user {budget.user.username}: {str(e)}", 
                        exc_info=True)
    
    # Log summary
    logger.info(f"Budget check task completed. Summary: "
                f"Processed {budget_count} budgets, "
                f"Sent {notifications_sent} notifications, "
                f"Encountered {errors} errors")
    
    return {
        'task_id': self.request.id,
        'date': today.isoformat(),
        'budgets_processed': budget_count,
        'notifications_sent': notifications_sent,
        'errors': errors
    }