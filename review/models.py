from django.db import models
from api.models import Account
from blog.models import Event, ReviewComment

class EventReviewers(models.Model):
   
    REVIEW_STATUS_PENDING = 'P'
    REVIEW_STATUS_COMPLETED = 'C'
    REVIEW_STATUS_CHOICES = [
        (REVIEW_STATUS_PENDING,'Pending'),
        (REVIEW_STATUS_COMPLETED,'Completed')
    ]
    event_id = models.ForeignKey(Event,on_delete=models.CASCADE,db_column='event_id',related_name='reviewers')
    assigned_reviewer_id = models.ForeignKey(Account,on_delete=models.CASCADE,db_column='assigned_reviewer_id',related_name='reviewers')
    author_id = models.ForeignKey(Account,on_delete=models.CASCADE,db_column='author_id',related_name='authors')
    assigned_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    review_status =models.CharField(max_length=10,choices=REVIEW_STATUS_CHOICES,default=REVIEW_STATUS_PENDING)
    archived = models.BooleanField(default=0)

class EventReviewLogs(models.Model):
    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_UNDER_REVIEW ='U'
    STATUS_SUBMITTED = 'S'
    STATUS_RESUBMITTED = 'RS'
    STATUS_REWORK = 'RW'
    STATUS_CHOICES =[
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_UNDER_REVIEW,'Under Review'),
        (STATUS_SUBMITTED,'Submitted'),
        (STATUS_RESUBMITTED,'Resubmitted'),
        (STATUS_REWORK,'Rework'),
    ]
    event_id = models.ForeignKey(Event,on_delete=models.CASCADE,db_column='event_id',related_name='logs')
    event_reviewer = models.ForeignKey(Account,on_delete=models.CASCADE)
    comment = models.ForeignKey(ReviewComment,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default=STATUS_SUBMITTED)

class EventContentWriter(models.Model):
    event_id = models.ForeignKey(Event,on_delete=models.CASCADE,db_column='event_id',related_name='content_writer')
    assigned_content_writer_id = models.ForeignKey(Account,on_delete=models.CASCADE,db_column='assigned_content_writer_id',related_name='content_writers')
    assigned_at = models.DateTimeField(auto_now_add=True)
    