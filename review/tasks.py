from celery import shared_task
from time import sleep
from .functions import block_user,send,archive_events
@shared_task   
def block_content_writer(id):
    sleep(5)
    block_user(id)
    return True
@shared_task
def send_email(email,subject,message):
    send(email,subject,message)
    return True
@shared_task
def archive_event(event_id):
    sleep(5)
    archive_events(event_id)
    return True
# celery -A anveshak_inhouse worker --loglevel=INFO