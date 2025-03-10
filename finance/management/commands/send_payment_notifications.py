# finance/management/commands/send_payment_notifications.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from finance.models import UpcomingPayment, User


class Command(BaseCommand):
    help = 'Send email notifications for upcoming payments'

    def handle(self, *args, **options):
        # Calculate the date 3 days from now
        notification_date = datetime.now().date() + timedelta(days=3)

        # Find all payments due in 3 days
        upcoming_payments = UpcomingPayment.objects.filter(
            date=notification_date)

        notifications_sent = 0

        # Send email for each payment
        for payment in upcoming_payments:
            user = payment.user
            try:
                profile = User.objects.get(email=user.email)
                if profile.notification and user.email:
                    subject = f"Upcoming Payment Reminder: {payment.category.name}"
                    message = f"""
                    Hi {user.firstname},

                    This is a reminder that you have an upcoming payment in 3 days:

                    Category: {payment.category.name}
                    Amount: {payment.amount}
                    Date: {payment.date}
                    Description: {payment.description}

                    Thank you for using MoneyBees!
                    """

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    notifications_sent += 1
            except User.DoesNotExist:
                # If the user doesn't have a profile, skip them
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Sent {notifications_sent} payment notifications')
        )
