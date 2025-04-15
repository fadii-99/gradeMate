from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from accounts.models import User
from accounts.auth_utils import generate_jwt_token, decode_jwt_token

support_email = 'support@portraiture.com'

def send_verification_email(username, email, token):
    # verification_url = f"http://localhost:3000/email-verified/{token}/"
    verification_url = f"http://207.154.243.174/email-verified/{token}"

    # Send verification email
    html_message = render_to_string('emailverification.html', {
        'username': username,
        'email': email,
        'verification_url': verification_url,
        'support_email': support_email
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject='Verify your email address',
        body=plain_message,  
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    email.attach_alternative(html_message, "text/html") 
    email.send()
 


def send_reset_password_email(username, email, token):
    verification_url = f"http://localhost:3000/reset-password/{token}/"
    # verification_url = f"http://207.154.243.174/reset-password/{token}"

    # Send verification email
    html_message = render_to_string('resetPassword.html', {
       'username': username,
        'email': email,
        'verification_url': verification_url,
        'support_email': support_email
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject='Verify your email address',
        body=plain_message,  
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    email.attach_alternative(html_message, "text/html")  # HTML version
    email.send()



def send_passcode_email(customer_email, passcode):
    # token = generate_jwt_token(user)
    # verification_url = f"http://localhost:3000/email-verified/{token}/"
    event_url = f"http://207.154.243.174S"

    # Send verification email
    html_message = render_to_string('passcode.html', {
        'passcode': passcode,
        'event_url': event_url,
        'support_email': support_email
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject='Seceret Passcode',
        body=plain_message,  
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer_email]
    )
    email.attach_alternative(html_message, "text/html") 
    email.send()

