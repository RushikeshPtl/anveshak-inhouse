from celery import shared_task
from time import sleep
from .functions import block_user,send_mail_to_reviewer
@shared_task   
def block_content_writer(id):
    sleep(5)
    block_user(id)
    return True
@shared_task
def send_mail(email):
    send_mail_to_reviewer(email)
    return True