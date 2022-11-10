from django.contrib import admin
from .models import EventReviewers,EventReviewLogs

# Register your models here.
admin.site.register(EventReviewLogs),
admin.site.register(EventReviewers)
