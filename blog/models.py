from django.db import models
from api.models import Account

class Title(models.Model):
    title = models.CharField(max_length = 255)
    country_of_origin = models.CharField(max_length=255,default="India")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'Title'


class Event(models.Model):
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
    title_id = models.ForeignKey(Title,on_delete=models.CASCADE,db_column='title_id',related_name='events')
    author_id= models.ForeignKey(Account,on_delete=models.CASCADE,db_column='author_id',related_name='events')
    status = models.CharField(max_length=12,choices=STATUS_CHOICES,default=STATUS_SUBMITTED)
    description = models.TextField()
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    is_saved = models.BooleanField(default=1)
    is_submitted = models.BooleanField(default=0)
    
    INSTAGRAM = 'I'
    FACEBOOK = 'F'
    WHATSAPP = 'W'
    TWITTER = 'T'
    TV = 'T'
    OTHER = 'O'
    STATUS_CHOICES_REFERENCES = [
        (INSTAGRAM,'Instagram'),
        (FACEBOOK,'facebook'),
        (WHATSAPP,'Whatsapp'),
        (TWITTER,'twitter'),
        (TV,'tv'),
        (OTHER,'other')
    ]
    references = models.CharField(max_length=12,choices=STATUS_CHOICES_REFERENCES)
    other = models.CharField(max_length=100,null=True)

    REQUIRED_FIELDS = ['title','description']
    class Meta:
        db_table = 'Event'

    def validation(self,id):
        role = Role.objects.filter(is_admin = 1,account_id=id)
        if len(role) > 0:
            if role[0].account_id == id:
                return True
        if id == self.author_id:
            return True
        return False


class Role(models.Model):
    account = models.OneToOneField(Account,on_delete=models.CASCADE,related_name='roles')
    is_admin = models.BooleanField(default=0)
    is_reviewer = models.BooleanField(default=0)
    is_content_writer = models.BooleanField(default=0)
    is_author = models.BooleanField(default=0)
    is_user = models.BooleanField(default=1)
    
    class Meta:
        db_table = 'Role'


class ReviewComment(models.Model):
    
    event_id = models.ForeignKey(Event,on_delete=models.CASCADE,db_column='event_id',related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PageReadLogs(models.Model):
    page = models.IntegerField(null = True)
    percentage = models.FloatField(null=True)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)