from django.core.mail import send_mail
from django.conf import settings

def send_budget_notification(user, budget, spent_amount):
    """
    Send a notification email when budget threshold is reached.
    """
    subject = f'Budget Alert: {budget.period.capitalize()} spending threshold reached'
    message = f"""
    Hello {user.username},

    Your {budget.period} budget of ${budget.amount} has reached the notification threshold.
    Current spending: ${spent_amount}
    Remaining budget: ${budget.amount - spent_amount}

    This is a friendly reminder to help you stay within your budget.

    Best regards,
    SpendSmart Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    ) 