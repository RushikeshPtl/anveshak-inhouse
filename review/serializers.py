from rest_framework import serializers
from api.models import Account
from blog.models import Event,Title,ReviewComment,Role
from .models import EventReviewers,EventContentWriter,EventReviewLogs
from blog.serializers import EventListSerializer,EventPostSerializer
from django.db.models import Count,Sum,Q
from django.db.models.functions import Concat
from blog.functions import get_user_role
from . import tasks
from rest_framework.response import Response


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','title_id','author_id','description','year','created_at','status']
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','title_id','author_id','description','year','created_at','status']

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
        event = Event.objects.filter(id = obj.event_id)
        title = Title.objects.filter(id = event[0].title_id_id)
        return title[0].title

    def get_event(self,obj):
        event = Event.objects.filter(id = obj.event_id)
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

        a = EventReviewers.objects.filter(archived=0,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event__status = 'U').values('event_id').annotate(Count('event_id'))

        if len(a) > 0:
            dict['Under Review'] = a[0].get('event_id__count')
        else:
            dict['Under Review'] = 0

        # a = EventReviewers.objects.filter(archived=0,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event__status = 'RW').values('event_id').annotate(Count('event_id'))
        # if len(a) > 0:
        #     dict['Rework'] = a[0].get('event_id__count')
        # else:
        #     dict['Rework'] = 0
            
        return dict
    
    def get_approved(self,obj):
        dict = {}
        a = EventReviewers.objects.filter(archived=0,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event__status = 'A').values('event_id').annotate(Count('event_id'))
        if len(a) > 0:
                return a[0].get('event_id__count')
        return 0
    
    def get_rejected(self,obj):
        a = EventReviewers.objects.filter(archived=0,assigned_reviewer_id = obj.get('assigned_reviewer_id')).filter(event__status = 'R').values('event_id').annotate(Count('event_id'))
        if len(a) > 0:
                return a[0].get('event_id__count')
        return 0

class EventContentWriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventContentWriter
        fields = ['event_id','assigned_content_writer_id']

    def validate(self, attrs):
        content_writer_id = attrs['assigned_content_writer_id']
        role = Role.objects.filter(account_id=content_writer_id).first()
        if role.is_content_writer:
            return attrs
        raise serializers.ValidationError('Provided id is not recognized as a content-writer.Please provide valid id for a content writer!')
class EventReviewLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model= EventReviewLogs
        fields = ['status','comment_id','event_reviewer_id','event_id']

class ContentWriterProfileSerializer(serializers.ModelSerializer):
    content_writer_id = serializers.SerializerMethodField()
    content_writer_name = serializers.SerializerMethodField()
    total_events_assigned = serializers.SerializerMethodField()
    total_approved_events = serializers.SerializerMethodField()
    total_rejected_events = serializers.SerializerMethodField()
    class Meta:
        model = EventContentWriter
        fields = ['content_writer_id','content_writer_name','total_events_assigned','total_approved_events','total_rejected_events']
    def get_content_writer_id(self,obj):
        cw_ids = Role.objects.values('account_id').filter(is_content_writer=1).all()
        print(cw_ids)
        for id in cw_ids:
            return id['account_id']
    def get_content_writer_name(self,obj):
        names = Account.objects.select_related('roles').values('first_name','last_name').filter(roles__is_content_writer=1).distinct()
        for i in names:
            name = i['first_name'] + ' ' + i['last_name']
            return name
    def get_total_events_assigned(self,obj):
        cw_id = self.context.get('cw_id')
        event_ids = EventContentWriter.objects.values('event_id').filter(assigned_content_writer_id=cw_id).all()
        events = Event.objects.filter(id__in=event_ids).all()
        serializer = EventSerializer(events,many=True)
        return len(serializer.data)
    def get_total_approved_events(self,obj):
        cw_id = self.context.get('cw_id')
        event_ids = EventContentWriter.objects.values('event_id').filter(assigned_content_writer_id=cw_id).all()
        approved_events = Event.objects.filter(id__in=event_ids,status='A').all()
        serializer = EventSerializer(approved_events,many=True)
        return len(serializer.data)
    def get_total_rejected_events(self,obj):
        cw_id = self.context.get('cw_id')
        event_ids = EventContentWriter.objects.values('event_id').filter(assigned_content_writer_id=cw_id).all()
        rejected_events = Event.objects.filter(id__in=event_ids,status='R').all()
        serializer = EventSerializer(rejected_events,many=True)
        return len(serializer.data)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('action') == 'list':
            data={
                'content_writer_id': representation.get('content_writer_id'),
                'content_writer_name': representation.get('content_writer_name')
            }
            return data
        elif self.context.get('action') == 'retrieve':
            representation['success_rate'] = str((representation['total_approved_events']/representation['total_events_assigned'])*100) + '%'
            if representation['total_rejected_events'] >= 10:
                cw_id = representation['content_writer_id']
                tasks.block_content_writer.delay(cw_id)
                representation["msg"] = "This Content Writer has been Blocked because of poor performance!"
                return representation  
            return representation