from django.shortcuts import get_object_or_404
from blog.models import Event, ReviewComment, Title
from blog.serializers import ReviewCommentSerializer, TitleSerializer,EventListSerializer,EventPostSerializer
import rest_framework 
from rest_framework.response import Response

class Titles:
    
    def get(self,request,pk=None):
        if pk is None:
            titles = Title.objects.all()
            titles_lst = []
            for title in titles:
                titles_lst.append(title.__dict__)
            serializer = TitleSerializer(data=titles_lst,many=True)
            serializer.is_valid(raise_exception=True)
            return serializer.data
        else:
            title = get_object_or_404(Title,pk=pk)
            serializer = TitleSerializer(data=title.__dict__)
            serializer.is_valid(raise_exception=True)
            return serializer.data
    
    def post(self,request):
        data = request.data
        serializer = TitleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

class Events:
    
    def get(self,request,pk=None):
        if pk is None:
            events = Event.objects.filter(status='A')
            event_lst = []
            for event in events:
                event_lst.append(event.__dict__)
            serializer = EventListSerializer(data=event_lst,many=True)
            serializer.is_valid(raise_exception=True)
            return serializer.data
        else:
            event = get_object_or_404(Event,pk=pk)
            serializer = EventListSerializer(data=event.__dict__)
            serializer.is_valid(raise_exception=True)
            return serializer.data
    
    def post(self,request):
        data = request.data
        serializer = EventPostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

class TitleEvents:
    
    def get(self,request,pk,status=None):
        title = get_object_or_404(Title,pk=pk)
        if status is not None:
            events = Event.objects.filter(title_id=pk,status=status).order_by('year')
        else:
            events = Event.objects.filter(title_id=pk).order_by('year')
        serializer = TitleSerializer(data=title.__dict__)
        serializer.is_valid(raise_exception=True)
        events_lst = []
        for event in events:
            events_lst.append(event.__dict__)
        events_serializer = EventListSerializer(data=events_lst,many=True)
        events_serializer.is_valid(raise_exception=True)
        comments = ReviewComment.objects.filter(event=pk,reviewer_status='A')
        comment_serializer = ReviewCommentSerializer(data=comments,many=True)
        comment_serializer.is_valid(raise_exception=True)
        data = {
                "title": {
                    "id": title.pk,
                    "title":title.title,
                    "country_of_origin": title.country_of_origin
                }, 
                "events": events_serializer.data,
                "comments": comment_serializer.data
        }
        return data
    
    def post(self,request):
        data = request.data
        serializer = EventPostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def patch(self,request,pk):
        event = get_object_or_404(Event,pk=pk)
        data = rest_framework.parsers.JSONParser().parse(request)
        serializer = EventPostSerializer(event,data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def delete(self,request,pk):
        event =get_object_or_404(Event,pk=pk)
        event.delete()
        return "event Deleted Successfully!"
    
class StandardResponse:
    def success_response(self,data,message,status):
        return Response(
            {
                "success": True,
                "Data" : data,
                "message":message
            },status=status
        )
    
    def http404_response(self,data,message,status):
        return Response(
            {
                "success": False,
                "Data" : None,
                "message":message
            },status=status
        )

    def validationerror_response(self,data,message,status):
        return Response(
            {
                "success": False,
                "Data" : None,
                "message":message
            },status=status
        )
