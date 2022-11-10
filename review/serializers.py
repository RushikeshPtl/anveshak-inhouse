from rest_framework import serializers
from api.models import Account
from blog.models import Event,Title,ReviewComment,Role
from .models import EventReviewers,EventReviewLogs
from blog.serializers import EventListSerializer,EventPostSerializer,status
from django.db.models import Count

class EventSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id','title_id','author_id','description','year','created_at','status']
        def get_status(self,obj):
            return status(obj.status)


class EventReviewersSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReviewers
        fields = '__all__'


class FetchEventReviewersSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['title','event']
        # fields = ['event']

    def get_title(self,obj):
        if "yes" == self.context.get('history').lower():
            event = Event.objects.filter(id = obj.event_id_id,status = 'A' or 'R')
        else:
            event = Event.objects.filter(id = obj.event_id_id)
            title = Title.objects.filter(id = event[0].title_id_id)
        return title[0].title

    def get_event(self,obj):
        if "yes" == self.context.get('history').lower():
            event = Event.objects.filter(id = obj.event_id_id,status = 'A' or 'R')
        else:
            event = Event.objects.filter(id = obj.event_id_id)
        event = EventListSerializer(event[0]).data
        return event


class FetchReviewerEventCountSerializer(serializers.ModelSerializer):
    assigned_reviewer_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    approved = serializers.SerializerMethodField()
    rejected = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['assigned_reviewer_id','name','total','approved','rejected']
        
    def get_name(self,obj):
        account = Account.objects.filter(id=obj.get('assigned_reviewer_id'))
        return " ".join([account[0].first_name,account[0].last_name])

    def get_assigned_reviewer_id(self,obj):
        return obj.get('assigned_reviewer_id')
    
    def get_total(self,obj):
        dict = {}
        dict['total'] = obj.get('total')

        a = EventReviewers.objects.filter(archived=0,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event_id__status = 'U').values('event_id').annotate(Count('event_id'))
        # print(a)
        if len(a) > 0:
            # dict['Under Review'] = a[0].get('event_id__count')
            dict['Under Review'] = len(a)
        else:
            dict['Under Review'] = 0

        dict['Under Review Percentage'] = (len(a) * 100) / obj.get('total')
        
        # a = EventReviewers.objects.filter(archived=0,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event_id__status = 'S').values('event_id').annotate(Count('event_id'))
        # if len(a) > 0:
        #     dict['Submitted'] = a[0].get('event_id__count')
        # else:
        #     dict['Submitted'] = 0
        return dict
    
    def get_approved(self,obj):
        dict = {}
        a = EventReviewers.objects.filter(archived=1,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event_id__status = 'A').values('event_id').annotate(Count('event_id'))
        if len(a) > 0:
            dict['Approved'] = len(a)
        else:
            dict['Approved'] = 0

        dict['Approved Percentage'] = (len(a) * 100) / obj.get('total')
        
        return dict

    def get_rejected(self,obj):
        dict = {}
        a = EventReviewers.objects.filter(archived=1,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event_id__status = 'R').values('event_id').annotate(Count('event_id'))
        if len(a) > 0:
                # return a[0].get('event_id__count')
            dict['Rejected'] = len(a)
        else:
            dict['Rejected'] = 0
            
        dict['Rejected Percentage'] = (len(a) * 100) / obj.get('total')
 
        return dict


class FetchEventReviewersLogSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['title','event']
        # fields = ['event']

    def get_title(self,obj):
        # print(obj.event_id.title_id.title)
        # title = Title.objects.filter(id = obj.event_id_id)
        return obj.event_id.title_id.title

    def get_event(self,obj):
        event = Event.objects.filter(id = obj.event_id_id)
        event = EventListSerializer(event[0]).data
        # print(event)

        reviewcomment = ReviewComment.objects.filter(event_id = event.get('id'))
        if len(reviewcomment) > 0:
            event['comment'] = ReviewCommentSerializer(reviewcomment[0]).data
            eventreviewlogs = EventReviewLogs.objects.filter(event_id=event.get('id'))
            event['log'] = EventReviewLogsSerializer(eventreviewlogs[0]).data
        # else:
        #     event['comment'] = "Reviwers didn't make any comment"
        #     event['log'] = "Reviwers didn't make any comment so dont have a log"
        # print(event)
        return event


class ReviewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = ['comment','created_at','updated_at']

   
class EventReviewLogsSerializer(serializers.ModelSerializer):
    status_before = serializers.SerializerMethodField()
    status_now = serializers.SerializerMethodField()
    class Meta:
        model = EventReviewLogs
        fields = ['id','comment','status_before','status_now','created_at','updated_at']
        
    def get_status_before(self,obj):
        return status(obj.status_before)
    
    def get_status_now(self,obj):
        return status(obj.status_now)