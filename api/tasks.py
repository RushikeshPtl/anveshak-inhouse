# from celery import shared_task
# from time import sleep
# # from . import classes
# from . import helpers

# @shared_task
# def deleteToken(email):
#     sleep(20)
#     # classes.deleteToken(email)
#     return None

# @shared_task
# def mailSent(email,password_reset):
#     helpers.send_forget_password_mail(email,password_reset)
#     # deleteToken.delay(email)
#     return True
from celery import shared_task
from time import sleep
# from . import classes
from . import helpers

@shared_task
def deleteToken(email):
    sleep(20)
    # classes.deleteToken(email)
    return None

@shared_task
def mailSent(email,password_reset):
    helpers.send_forget_password_mail(email,password_reset)
    # deleteToken.delay(email)
    return True
