from django.shortcuts import get_object_or_404
from blog.models import Event, ReviewComment, Title
from blog.serializers import ReviewCommentSerializer, TitleSerializer,EventListSerializer,EventPostSerializer
import rest_framework 
from rest_framework.response import Response
    
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
