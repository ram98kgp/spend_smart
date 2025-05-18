from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

def send_budget_notification(user, budget, current_spent):
    """
    Send budget notification email to user
    """
    subject = 'Budget Alert: Spending Threshold Reached'
    message = f"""
    Dear {user.username},

    Your grocery spending has reached the notification threshold.

    Budget Details:
    - Period: {budget.period}
    - Total Budget: {budget.currency_symbol}{budget.amount}
    - Notification Threshold: {budget.currency_symbol}{budget.notification_threshold}
    - Current Spent: {budget.currency_symbol}{current_spent}
    - Remaining Budget: {budget.currency_symbol}{budget.amount - current_spent}
    - Currency: {budget.get_currency_display()}

    Please review your spending and adjust accordingly.

    Best regards,
    SpendSmart Team
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    ) 