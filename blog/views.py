from rest_framework.viewsets import ModelViewSet
from blog.renderers import CustomRenderer
from .models import Event, ReviewComment, Role, Title, PageReadLogs
from blog.serializers import AdminTitleSerializer,TitleSerializer,EventSerializer, AuthorTitleSerializer, ReviewCommentSerializer, ReviewerTitleSerializer, RoleSerializer,ContentWriterTitleSerializer,UserTitleSerializer,UserEventSerializer,AdminEventSerializer,ReviewerEventSerializer,ContentWriterEventSerializer,AuthorEventSerializer,BlogSerializer, EventPostSerializer, SortTitleEventSerializer
from .permissions import IsAdmin,IsAuthor,IsContentWriter,IsReviewer,IsUser
from blog.functions import get_user_role
from blog.classes import StandardResponse
from rest_framework import status
from rest_framework.decorators import permission_classes
import rest_framework
from rest_framework.views import APIView
from api.models import Account
from api.serializers import AccountSerializer
from django.http import HttpResponse
import json

# Adding the title in view set
class TitleViewSet(ModelViewSet):
    renderer_classes = [CustomRenderer]
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

    def get_permissions(self):
        role = get_user_role(self)
        if role == 'admin':
            return [IsAdmin()]
        elif role == 'reviewer':
            return [IsReviewer()]
        elif role == 'author':
            return [IsAuthor()]
        elif role == 'content writer':
            return [IsContentWriter()]
        elif role == 'user':
            return [IsUser()]
    
    def get_serializer_context(self):
        try:
            title_id = self.kwargs['title_pk']
        except KeyError:
            title_id = None
        role = get_user_role(self)
        return {'account_id':self.request.user.id,'title_id':title_id,'user_role':role}

class EventViewSet(ModelViewSet):
    renderer_classes = [CustomRenderer]
    serializer_class = EventSerializer
    def get_queryset(self):
        user_id = self.request.user.id
        try:
            title_id = self.kwargs['title_pk']
        except KeyError:
            title_id = None
        role = get_user_role(self)
        if role == 'user':
            return Event.objects.filter(title_id=title_id,status='A',is_submitted=1).all()
        elif role == 'author':
            return Event.objects.filter(title_id=title_id,author_id=user_id).all()
        elif role == 'content writer':
            event_ids = EventContentWriter.objects.values('event_id').filter(assigned_content_writer_id=user_id)
            return Event.objects.filter(title_id=title_id,id__in=event_ids).all()
        elif role == 'reviewer':
            event_ids = EventReviewers.objects.values('event_id').filter(assigned_reviewer_id=user_id)
            return Event.objects.filter(title_id=title_id,id__in=event_ids)
        elif title_id == None:
            return Event.objects.all()
        return Event.objects.filter(title_id=title_id).all()
    
    def get_permissions(self):
        role = get_user_role(self)
        if role == 'admin':
            return [IsAdmin()]
        elif role == 'reviewer':
            return [IsReviewer()]
        elif role == 'author':
            return [IsAuthor()]
        elif role == 'content writer':
            return [IsContentWriter()]
        elif role == 'user':
            return [IsUser()]
    

    def get_serializer_context(self):
        try:
            title_id = self.kwargs['title_pk']
        except KeyError:
            title_id = None
        role = get_user_role(self)
        return {'author_id':self.request.user.id,'title_id':title_id,'user_role':role,'request':self.request.method}
    
class ReviewCommentViewSet(ModelViewSet):
    queryset = ReviewComment.objects.all()
    serializer_class = ReviewCommentSerializer
    permission_classes = [IsReviewer]


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


# return the event if only the admin and particular author requested
@permission_classes([rest_framework.permissions.IsAuthenticated,])
class AuthorView(APIView):

    def get(self,request,format="json"):

        event = Event.objects.filter(id=self.request.data.get("event_id"))

        if event[0].validation(request.user.id):
            return StandardResponse.success_response(self,data = {"HI":"HI"},message="Data Fetched Successfully!",status=status.HTTP_200_OK)
        return StandardResponse.success_response(self,data = {"":""},message="Data Not Fetched Successfully!",status=status.HTTP_200_OK)


# Fetching the all event title wise of particular account
@permission_classes([rest_framework.permissions.IsAuthenticated,])
class FetchAllBlog(APIView):

    def get(self,request,format="json"):
        account = Account.objects.filter(id=self.request.data.get("id"))
        if not account.exists():
            return StandardResponse.success_response(self,data = {"":""},message="User not Found",status=status.HTTP_200_OK)

        blog = BlogSerializer(account[0]).data
        return StandardResponse.success_response(self,data = blog,message="Users event Title wise fetched successfully!",status=status.HTTP_200_OK)


# returns the account role wise
@permission_classes([rest_framework.permissions.IsAuthenticated,IsAdmin])
class FetchRoleWiseAccount(APIView):
    
    def get(self,obj,format="json"):
        if 'admin' == self.request.data.get("role").lower():
            account = Account.objects.filter(roles__is_admin = 1)
        elif 'reviewer' == self.request.data.get("role").lower():
            account = Account.objects.filter(roles__is_reviewer = 1)
        elif 'content writer' == self.request.data.get("role").lower():
            account = Account.objects.filter(roles__is_content_writer = 1)
        elif 'author' == self.request.data.get("role").lower():
            account = Account.objects.filter(roles__is_author = 1)            

        data = AccountSerializer(account,many=True).data

        return StandardResponse.success_response(self,data = data,message="Users event Title wise fetched successfully!",status=status.HTTP_200_OK)


class FetchSortedEvent(APIView):
    # asc = Old to latest       or      a to z
    # desc = latest to old      or      z to a

    def get(self, request,format = "json"):

        if "event" == self.request.data.get("sort_title").lower():
            if "asc" == self.request.data.get("sort").lower():
                # Sorting Event old to latest
                event = Event.objects.order_by('created_at')
            else:
                # Sorting Event lates to old
                event = Event.objects.order_by('-created_at')
            
            event = EventPostSerializer(event,many=True).data

        elif "title" == self.request.data.get("sort_title").lower():
            if "asc" == self.request.data.get("sort").lower():
                # Sorting Event title wise A to Z
                event = Title.objects.order_by('title')
            else:
                # Sorting Event title wise Z to A
                event = Title.objects.order_by('-title')
            # dummy query
            # event = Event.objects.select_related('title_id')
            event = SortTitleEventSerializer(event,many=True).data

        else:
            return HttpResponse("Provide valid \"sort_title\ and \"sort\"")  

        event = json.dumps(event)
        return HttpResponse(event, content_type = 'application/json/')


# Post and get page blog reading history
@permission_classes([rest_framework.permissions.IsAuthenticated,])
class PageReadLog(APIView):
    def post(self, request):
        if not self.request.user.id:
            return HttpResponse("login first and provide user")
        if not self.request.data.get("page") and not self.request.data.get("percentage") :
            return HttpResponse("Provide Reading history")
        if not self.request.data.get("event_id"):
            return HttpResponse("Provide event_id")

        pagereadlogs = PageReadLogs()
        if not self.request.data.get("percentage"):
            pagereadlogs.page = self.request.data.get("page")
        else:
            pagereadlogs.percentage = self.request.data.get("percentage")

        pagereadlogs.event_id = self.request.data.get("event_id")
        pagereadlogs.account_id = self.request.user.id
        pagereadlogs.save()
        
        return HttpResponse("Page History save succesfully")


    def get(self,request):
        pagereadlogs = PageReadLogs.objects.filter(event_id=self.request.data.get("event_id"),account_id = self.request.user.id)
        if len(pagereadlogs) > 0:
            data = {}
            if pagereadlogs[0].page:
                data['page'] = pagereadlogs[0].page
            else:
                data['percentage'] = pagereadlogs[0].percentage

            data['event_id'] = pagereadlogs[0].event_id
            data['account_id'] = pagereadlogs[0].account_id
            data = json.dumps(data)
            return HttpResponse(data, content_type = 'application/json/')
        return HttpResponse("their is no page read logs")
    
    
