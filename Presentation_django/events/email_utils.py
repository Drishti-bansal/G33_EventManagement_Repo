from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_booking_confirmation_email(booking, event):
    """
    Send a booking confirmation email to the user
    """
    subject = f'Your Booking Confirmation - {event.title}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = booking.user_email
        
    context = {
        'booking': booking,
        'event': event,
    }
        
    html_content = render_to_string('emails/booking_confirmation.html', context)
    text_content = strip_tags(html_content)  
        
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
        
    try:
        email.send()
        logger.info(f"Confirmation email sent to {to_email} for booking {booking.id}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        print(f"Error sending email: {e}")
        return False