from api.models import Account
from django.conf import settings
from django.core.mail import send_mail

def block_user(id):
    Account.objects.filter(id=id).update(is_active=0)
    return True

def send_mail_to_reviewer(email):
    subject = 'Task Assigned'
    message = f'Hello, You got an event to review!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True