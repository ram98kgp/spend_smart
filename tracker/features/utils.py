from django.core.mail import send_mail
from django.conf import settings

def send_budget_notification(user, budget, spent_amount):
    """
    Send a notification email when budget threshold is reached.
    """
    subject = f'Budget Alert: {budget.currency_symbol}{spent_amount} spent of {budget.currency_symbol}{budget.amount}'
    message = f"""
    Hello {user.username},

    Your {budget.period} grocery budget has reached the notification threshold.

    Budget Details:
    - Total Budget: {budget.currency_symbol}{budget.amount}
    - Amount Spent: {budget.currency_symbol}{spent_amount}
    - Notification Threshold: {budget.currency_symbol}{budget.notification_threshold}

    Please review your spending and adjust accordingly.

    Best regards,
    Your SpendSmart Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    ) 