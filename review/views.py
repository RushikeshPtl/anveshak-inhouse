from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from blog.models import Event,ReviewComment,Role
from blog.renderers import CustomRenderer
from .models import EventReviewers,EventContentWriter,EventReviewLogs
from .serializers import EventReviewersSerializer,EventSerializer,FetchEventReviewersSerializer,FetchReviewerEventCountSerializer,EventContentWriterSerializer,ContentWriterProfileSerializer
from blog.serializers import  ReviewCommentSerializer
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
# To get list of events assigned to particular reviewer
class ReviewerAssignedEventsViewSet(ModelViewSet):
    http_method_names = ['get','post','put','patch']
    renderer_classes = [CustomRenderer]
    permission_classes = [IsReviewer]
    serializer_class = EventSerializer
    def get_queryset(self):
        reviewer_id = self.request.user.id
        assigned_event_ids = EventReviewers.objects.values('event_id').filter(assigned_reviewer_id=reviewer_id)
        try:
            event_id = self.kwargs['pk']
        except KeyError:
            event_id = None
        # Changing Archieved status
        if self.request.method == 'PATCH':
            EventReviewers.objects.filter(event_id=event_id).update(archived=1)
        return Event.objects.filter(id__in=assigned_event_ids).all()
    
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
    # def create(self, request, *args, **kwargs):
    #     event_id = request.data['event_id']
    #     reviewer_id = request.user.id
    #     comment_id = ReviewComment.objects.values('id').last()['id']
    #     status_before = Event.objects.values('status').filter(id=event_id)
    #     status_now = Event.objects.values('status').filter(id=event_id)
    #     EventReviewLogs.objects.create(event_id_id=event_id,event_reviewer_id=reviewer_id,comment_id=comment_id,status_before=status_before,status_now=status_now)
    #     return super().create(request, *args, **kwargs)
@receiver(post_save, sender=ReviewComment)
def create_event_review_logs(sender,instance=None,created=False,**kwargs):
    if created:
        comment_id=instance.id
        event_id =instance.event_id
        event_reviewer_id = EventReviewers.objects.values('assigned_reviewer_id').filter(event_id=event_id).first()['assigned_reviewer_id']
        status = Event.objects.values('status').filter(id=event_id).first()['status']
        EventReviewLogs.objects.create(comment_id=comment_id,event_id=event_id,event_reviewer_id=event_reviewer_id,status=status)
        instance.save()

# To get List of events authored by him which have status in  Rework,Rejected,Under Review, Approved 
class AuthorViewSet(ModelViewSet):
    http_method_names = ['get','post','patch']
    serializer_class = EventSerializer
    permission_classes = [IsAuthor]
    renderer_classes = [CustomRenderer]
    def get_queryset(self):
        author_id = self.request.user.id
        if self.request.method == 'PATCH':
            Event.objects.filter(id=self.kwargs.get('pk'),is_submitted=1).update(status='RS')
            return Event.objects.filter(author_id=author_id)
        return Event.objects.filter(author_id=author_id)
    def get_serializer_context(self):
        return {'author_id':self.request.user.id}
    
@permission_classes([rest_framework.permissions.IsAuthenticated,IsAdmin])
class AssignReviewer(APIView):
    def post(self,request,format="json"):
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
                            return StandardResponse.success_response(self,data = {"":""},message="The reviewer for particular event is already exits",status=status.HTTP_200_OK)
                        eventreviewers.archived = 1
                        eventreviewers.save()

                    eventreviewers = EventReviewers(event_id_id=event.id,assigned_reviewer_id_id=self.request.data.get("reviewer_id"),author_id=event.author_id)
                    
                    #sending mail to assigned reviewer
                    reviewer = Account.objects.filter(id=self.request.data.get("reviewer_id")).first()
                    email = reviewer.email
                    tasks.send_mail.delay(email)


                    eventreviewers.save()
                    event.status = "U"
                    event.save()
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
