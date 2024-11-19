
from django.core.mail import send_mail
from django.conf import settings


def send_signup_email(user_email, username):
    """
    Sends a welcome email to the user after signup.
    """
    subject = "Welcome to Our Platform!"
    message = f"Hi {username},\n\nThank you for signing up! We are excited to have you on board.\n\nBest regards,\nTeam"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

def notify_customer(order):
    customer_email = order.customer.user.email
    subject = f"Your Order #{order.id} has been shipped!"
    message = (
        f"Dear {order.customer.user.username},\n\n"
        f"Good news! Your order with ID #{order.id} has been shipped.\n"
        f"You can expect your delivery soon.\n\n"
        f"Thank you for shopping with us!\n\n"
        f"Best regards,\n"
        f"Your Company Team"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [customer_email]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )

def notify_company(order):
    for item in order.items.all():
        company_email = item.product.company.user.email
        subject = f"New Order for Your Product: {item.product.name}"
        message = (
            f"Dear {item.product.company.name},\n\n"
            f"Your product '{item.product.name}' has been ordered by a customer.\n"
            f"Order ID: {order.id}\n"
            f"Quantity: {item.quantity}\n\n"
            f"Please review the order and prepare it for shipment.\n\n"
            f"Thank you,\n"
            f"Your Platform Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [company_email]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )