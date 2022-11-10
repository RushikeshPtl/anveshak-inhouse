from django.core.mail import send_mail
import uuid
from django.conf import settings
# from polibhaji import celery
# from .tasks import deleteToken

def send_forget_password_mail(email,password_reset):
    subject = 'You forget password link'
    message = f'Hi, This is yout token for your password {password_reset}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    # deleteToken.delay(user.email)
    return True