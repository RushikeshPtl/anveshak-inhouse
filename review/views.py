from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from blog.models import Event,ReviewComment,Role
from blog.renderers import CustomRenderer
from .models import EventReviewers,EventContentWriter,EventReviewLogs
from .serializers import EventReviewersSerializer,FetchEventReviewersSerializer,FetchReviewerEventCountSerializer,EventContentWriterSerializer,ContentWriterProfileSerializer,EventSerializer
from blog.serializers import  ReviewCommentSerializer
from rest_framework.viewsets import ModelViewSet
from blog.models import Event,ReviewComment,Role
from blog.renderers import CustomRenderer
from .models import EventReviewers, EventReviewLogs
from .serializers import EventReviewersSerializer,FetchEventReviewersSerializer,FetchReviewerEventCountSerializer
from blog.serializers import AdminTitleSerializer, AuthorTitleSerializer, ReviewCommentSerializer, ReviewerTitleSerializer, RoleSerializer,ContentWriterTitleSerializer,UserTitleSerializer,UserEventSerializer,AdminEventSerializer,ReviewerEventSerializer,ContentWriterEventSerializer,AuthorEventSerializer
from blog.permissions import IsAdmin,IsAuthor,IsContentWriter,IsReviewer,IsUser
from blog.functions import get_user_role
from blog.classes import StandardResponse
from rest_framework import status
from rest_framework.decorators import permission_classes
import rest_framework
from rest_framework.views import APIView
from django.db.models import Count
from django.dispatch import receiver
from django.db.models.signals import post_save
from api.models import Account
from . import tasks
from django.http import HttpResponse
import json

# To get list of events assigned to particular reviewer
class ReviewerAssignedEventsViewSet(ModelViewSet):
    http_method_names = ['get','patch']
    renderer_classes = [CustomRenderer]
    permission_classes = [IsReviewer]
    serializer_class = EventSerializer

    def get_queryset(self):
        reviewer_id = self.request.user.id
        assigned_event_ids = EventReviewers.objects.values('event_id').filter(assigned_reviewer_id=reviewer_id)
        return Event.objects.filter(id__in=assigned_event_ids).all()
    def partial_update(self, request, *args, **kwargs):
        if "status" in request.data:
            event = Event.objects.filter(id=self.kwargs['pk']).first()
            author_id = event.author_id.id
                 
            author = Account.objects.filter(id=author_id).first()
            email = author.email
            subject = f"Status of your event has been changed!"
            message = f"""
                        Hello{author.first_name} {author.last_name},
                        The status of your Event with an id of {self.kwargs['pk']} has been changed to {request.data['status']}
                        """
            tasks.send_email.delay(email,subject,message)
            if request.data['status'] == 'A' or request.data['status'] == 'R':
                tasks.archive_event.delay(event_id=self.kwargs['pk'])
        return super().partial_update(request, *args, **kwargs)
    def get_serializer_context(self):
        role = get_user_role(self)
        user_id=self.request.user.id
        return {'user_id': user_id,"role":role}
# To post comments on an event
class ReviewerCommentsViewSet(ModelViewSet):
    renderer_classes = [CustomRenderer]
    permission_classes = [IsReviewer]
    def get_queryset(self):
        reviewer_id = self.request.user.id
        try:
            event_id = self.kwargs['assigned_event_pk']
        except KeyError:
            event_id = None
        assigned_event_ids = EventReviewers.objects.values('event_id').filter(assigned_reviewer_id=reviewer_id)
        return ReviewComment.objects.filter(event_id__in=assigned_event_ids,event_id=event_id).all()
    serializer_class = ReviewCommentSerializer

# @receiver(post_save, sender=ReviewComment)
# def create_event_review_logs(sender,instance=None,created=False,**kwargs):
#     if created:
#         comment_id=instance.id
#         event_id =instance.event_id
#         event_reviewer_id = EventReviewers.objects.values('assigned_reviewer_id').filter(event_id=event_id).first()['assigned_reviewer_id']
#         status = Event.objects.values('status').filter(id=event_id).first()['status']
#         EventReviewLogs.objects.create(comment_id=comment_id,event_id=event_id,event_reviewer_id=event_reviewer_id,status=status)
#         instance.save()

# To get List of events authored by him which have status in  Rework,Rejected,Under Review, Approved 
class AuthorViewSet(ModelViewSet):
    http_method_names = ['get','post','patch']
    serializer_class = EventSerializer
    permission_classes = [IsAuthor]
    renderer_classes = [CustomRenderer]
    def get_queryset(self):
        author_id = self.request.user.id
        return Event.objects.filter(author_id=author_id)
    def get_serializer_context(self):
        try:
            event_id = self.kwargs['pk']
        except KeyError:
            event_id = None
        return {'author_id':self.request.user.id,'event_id':event_id}
    def create(self, request, *args, **kwargs):
        if "is_submitted" in request.data:
            if request.data['is_submitted'] == 1:
                pass
        return super().create(request, *args, **kwargs)
    def partial_update(self, request, *args, **kwargs):
        if "description" in request.data or "year" in request.data:
            event_id = self.kwargs['pk']
            Event.objects.filter(id=event_id).update(status="RS")
        return super().partial_update(request, *args, **kwargs)
    
@permission_classes([rest_framework.permissions.IsAuthenticated,IsAdmin])
class AssignReviewer(APIView):
    def post(self,request,format="json"):

        event_id = request.data['event_id']
        event = Event.objects.filter(id=event_id).first()
        if event.is_submitted != 1:
            return StandardResponse.http404_response(self,data=None,status=status.HTTP_400_BAD_REQUEST,message="This event is not submitted Yet!")

        role = Role.objects.filter(account_id=self.request.data.get("reviewer_id"),is_reviewer=1)            
        if len(role)>0:
            count = EventReviewers.objects.filter(assigned_reviewer_id=self.request.data.get("reviewer_id"),archived=0)
            if len(count)<10 :
                event = Event.objects.filter(id=self.request.data.get("event_id"))
                if len(event) > 0:
                    event = event[0]
                    eventreviewers = EventReviewers.objects.filter(event_id=self.request.data.get("event_id"),archived=0)
                    if len(eventreviewers)>0:
                        eventreviewers = eventreviewers[0]
                        if eventreviewers.assigned_reviewer_id == self.request.data.get("reviewer_id"):
                            return StandardResponse.success_response(self,data = {"":""},message="The revivwer for particular event is already exits",status=status.HTTP_200_OK)
                        eventreviewers.archived = 1
                        eventreviewers.save()

                    eventreviewers = EventReviewers(event_id_id=event.id,assigned_reviewer_id_id=self.request.data.get("reviewer_id"),author_id=event.author_id)
                    
                    #sending mail to assigned reviewer
                    reviewer = Account.objects.filter(id=self.request.data.get("reviewer_id")).first()
                    email = reviewer.email
                    subject = f"A new task has been assigned to you"
                    message = f"""
                                Hello{reviewer.first_name} {reviewer.last_name},
                                     Event with an id of {event_id} is assigned to you for a review!
                                      """
                    tasks.send_email.delay(email,subject,message)
                    eventreviewers.save()
                    event.status = "U"
                    event.save()

                    # sending mail to author 
                    event = Event.objects.filter(id=request.data['event_id']).first()
                    author_id = event.author_id.id
                 
                    author = Account.objects.filter(id=author_id).first()
                    email = author.email
                    subject = f"Status of your event has been changed!"
                    message = f"""
                                Hello{author.first_name} {author.last_name},
                                     The status of your Event with an id of {event_id} has been changed to "Under Review"
                                      """
                    tasks.send_email.delay(email,subject,message)

                    return StandardResponse.success_response(self,data = {"":""},message="Reviwer assigned Succesfully",status=status.HTTP_200_OK)
                return StandardResponse.success_response(self,data = {"":""},message="Wrong event id",status=status.HTTP_400_BAD_REQUEST)
            return StandardResponse.success_response(self,data = {"":""},message="Revivwer already have 10 events assigned",status=status.HTTP_400_BAD_REQUEST)
        return StandardResponse.success_response(self,data = {"":""},message="Please Enter Valid Reviwer",status=status.HTTP_400_BAD_REQUEST)

@permission_classes([rest_framework.permissions.IsAuthenticated,IsReviewer])
class FetchReviewerEvent(APIView):
    def get(self,request,format="json"):
        eventreviewers = EventReviewers.objects.filter(assigned_reviewer_id = request.user.id)

        data = FetchEventReviewersSerializer(eventreviewers,many=True).data
        return StandardResponse.success_response(self,data = data,message="Reviwer event succesfully",status=status.HTTP_200_OK)
    
@permission_classes([rest_framework.permissions.IsAuthenticated,IsAdmin])
class FetchReviewerEventCount(APIView):
    def get(self,request,format="json"):
        data = EventReviewers.objects.filter(archived=0).values('assigned_reviewer_id').annotate(total=Count('event_id'))
        data = FetchReviewerEventCountSerializer(data,many=True).data
        return StandardResponse.success_response(self,data = data ,message="Please Enter Valid Reviwer",status=status.HTTP_200_OK)  

# Content-writer 
class AssignContentWriter(ModelViewSet):
    http_method_names = ['post']
    permission_classes = [IsAdmin]
    serializer_class = EventContentWriterSerializer
    queryset = EventContentWriter.objects.all()
    renderer_classes = [CustomRenderer]

class ContentWriterProfileViewSet(ReadOnlyModelViewSet):
    queryset = EventContentWriter.objects.all()
    serializer_class = ContentWriterProfileSerializer
    renderer_classes = [CustomRenderer]
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):   
        return super().retrieve(request, *args, **kwargs)
    
    def get_serializer_context(self):
        try:
            content_writer_id = self.kwargs['pk']
        except KeyError:
            content_writer_id=None
        return {'action':self.action,'cw_id':content_writer_id}

@permission_classes([rest_framework.permissions.IsAuthenticated,IsReviewer])
class FetchReviewerEvent(APIView):
    def get(self,request,format="json"):
        if "yes" == self.request.data.get('history').lower():
            eventreviewers = EventReviewers.objects.filter(assigned_reviewer_id = request.user.id,archived = 1)
        else:
            eventreviewers = EventReviewers.objects.filter(assigned_reviewer_id = request.user.id,archived = 0)

        data = FetchEventReviewersSerializer(eventreviewers,many=True,context={'history': request.data.get('history')}).data

        return StandardResponse.success_response(self,data = data,message="Reviwer event succesfully",status=status.HTTP_200_OK)

class FetchReviewerEventCount(APIView):
    permission_classes = [IsAdmin | IsReviewer]
    def get(self,request,format="json"):
        
        role = Role.objects.filter(account_id=request.user.id)

        if role[0].is_admin == True:
            data = EventReviewers.objects.filter(archived=0).values('assigned_reviewer_id').annotate(total=Count('event_id'))
        else:
            data = EventReviewers.objects.filter(assigned_reviewer_id=request.user.id,archived=0).values('assigned_reviewer_id').annotate(total=Count('event_id'))

        data = FetchReviewerEventCountSerializer(data,many=True).data
        return StandardResponse.success_response(self,data = data ,message="Please Enter Valid Reviwer",status=status.HTTP_200_OK)

@permission_classes([rest_framework.permissions.IsAuthenticated,IsReviewer])
class FetchEventReviewersLog(APIView):
    
    def get(self,request,format="json"):
        eventreviewer = EventReviewers.objects.filter(assigned_reviewer_id=request.user.id).select_related('event_id')
        # data = FetchEventReviewersLogSerializer(eventreviewer,many = True).data
        data = json.dumps(data)
        return HttpResponse(data, content_type = 'application/json/')

@permission_classes([rest_framework.permissions.IsAuthenticated,IsReviewer])
class EventStatus(APIView):
    def post(self,request,format="json"):
        eventreviewers = EventReviewers.objects.filter(assigned_reviewer_id=self.request.user.id,archived=0).filter(event_id = self.request.data.get("event_id"))

        if len(eventreviewers) > 0:
            # print(eventreviewers[0])
            eventreviewers = eventreviewers[0]
            event = eventreviewers.event_id

            if "status_approved" == self.request.data.get("status").lower() or "status approved" == self.request.data.get("status").lower():
                event.status = 'A'
                eventreviewers.archived = 1
                eventreviewers.save()
                event.save()

            elif "status_rejected" == self.request.data.get("status").lower() or "status rejected" == self.request.data.get("status").lower():
                event.status = 'R'
                eventreviewers.archived = 1
                eventreviewers.save()
                event.save()

            elif "status_rework" == self.request.data.get("status").lower() or "status_rework" == self.request.data.get("status").lower():
                event.status = 'RW'
                event.save()

            return HttpResponse("Succesfullu updated!!")

        return HttpResponse("You are not authorzied")
    
    
    
    
