from api.models import Account
from django.conf import settings
from django.core.mail import send_mail
from blog.models import Event
from review.models import EventReviewers

def block_user(id):
    Account.objects.filter(id=id).update(is_active=0)
    return True

def send(email,subject,message):
    subject = subject
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def archive_events(event_id):
    EventReviewers.objects.filter(event_id=event_id).update(archived=1,review_status='C')
    return True
