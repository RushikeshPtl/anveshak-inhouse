from rest_framework import serializers
from .models import ReviewComment, Role, Title, Event
from api.models import Account
from review.models import EventReviewers

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        user_role = self.context.get('user_role')
        representation = super().to_representation(instance)
        if user_role == 'admin':
            return representation
        else:
            representation_data = {
            "id" : representation['id'],
            "title" : representation['title'],
            "country_of_origin" : representation['country_of_origin']
            }
            return representation_data
            
    def to_internal_value(self, data):
         return super().to_internal_value(data)

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
    def to_representation(self, instance):
        user_role = self.context.get('user_role')
        representation = super().to_representation(instance)
        representation_data = {
            "id" : representation['id'],
            "author_id" : representation['author_id'],
            "title_id" : representation['title_id'],
            "description" : representation['description'],
            "year" : representation['year'],
            "status" : representation['status']
            }
        if user_role == 'admin':
            return representation
        elif user_role == 'reviewer':
            return representation_data
        elif user_role == 'content writer':
            return representation_data
        elif user_role == 'author':
            return representation_data
        elif user_role == 'user':
            return representation_data
    def to_internal_value(self, data):
        user_role = self.context.get('user_role')
        try:
            
            resource_data = {
                "author_id" : data['author_id'],
                "title_id" : data['title_id'],
                "description" : data['description'],
                "year" : data['year']
            }
            if self.context.get('request') in ['POST','PUT']:
                return super().to_internal_value(resource_data)

        except:
            try:
                if user_role == 'content writer':
                    cw_data = {'description':data['description'],'is_submitted':data['is_submitted']}
                    return super().to_internal_value(cw_data)
                elif user_role == 'reviewer':
                    rwr_data = {'status':data['status']}
                    return super().to_internal_value(rwr_data)
            except:
                return ({"unauthorized":"You are not authorized to perform this action!"})
        
        if user_role == 'admin':
            return super().to_internal_value(data)
        elif user_role == 'reviewer':
            return super().to_internal_value(resource_data)
class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','author_id','description','year','status']

class EventPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title_id','author_id','description','year']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ReviewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = '__all__'


class UserTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['id', 'title']


class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','title_id','description']


class AdminTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'


class AdminEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class ReviewerTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'


class ReviewerEventSerializer(serializers.ModelSerializer):
    comments = ReviewCommentSerializer(many=True)
    class Meta:
        model = Event
        fields = ['id','title_id','author','description','year','created_at','status','comments']


class ContentWriterTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['id','title']


class ContentWriterEventSerializer(serializers.ModelSerializer):
    # title_id = serializers.CharField(read_only=True)
    class Meta:
        model = Event
        fields = ['title_id','description']


class AuthorTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['id','title']


class AuthorEventSerializer(serializers.ModelSerializer):   
    status = serializers.CharField(read_only=True)
    comments = ReviewCommentSerializer(many=True,read_only=True)
    class Meta:
        model = Event
        fields = ['id','title_id','author_id','description','year','status','comments','references','other']


class BlogSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = ('id','first_name','last_name','middle_name','email','phone','gender','title')
    def get_title(self,obj):
        title = Title.objects.filter(events__author_id=obj.id).distinct()
        event = TitleEventSerializer(title,many=True,context={'id': obj.id}).data
        return event


class TitleEventSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['title','event']
    def get_title(self,obj):
        return obj.title
    def get_event(self,obj):
        event = Event.objects.filter(title_id = obj.id,author_id = self.context.get('id') )
        event = EventListSerializer(event,many=True).data
        return event


class SortTitleEventSerializer(serializers.ModelSerializer):
    
    title = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['title','event']
        
    def get_title(self,obj):
        print(obj.title)
        return obj.title
    
    def get_event(self,obj):
        event = Event.objects.filter(title_id = obj.id)
        event = EventPostSerializer(event,many=True).data
        return event
    
# class
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