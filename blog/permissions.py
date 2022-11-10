from rest_framework import permissions
from .models import Role
from django.shortcuts import get_object_or_404

class IsAdmin(permissions.BasePermission):
    def has_permission(self,request,view):
        role_obj = get_object_or_404(Role,account=request.user.id)
        return bool(request.user and request.user.is_staff and role_obj.is_admin)

class IsAdmin(permissions.BasePermission):
    def has_permission(self,request,view):
        return bool(request.user and request.user.is_staff)
        
class IsReviewer(permissions.BasePermission):
    def has_permission(self, request, view):
        role_obj = get_object_or_404(Role,account=request.user.id)
        return bool(request.method in ['GET','HEAD','OPTIONS','POST','PUT','PATCH'] and request.user and role_obj.is_reviewer)
        
class IsContentWriter(permissions.BasePermission):
    def has_permission(self, request, view):
        role_obj = get_object_or_404(Role,account=request.user.id)
        return bool(request.method in ['GET','HEAD','OPTIONS','PATCH'] and request.user and role_obj.is_content_writer)
        
class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
       
        role_obj = get_object_or_404(Role,account=request.user.id)
        return bool(request.method in ['GET','HEAD','OPTIONS','POST','PUT','PATCH','DELETE'] and request.user and role_obj.is_author)

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in ['GET','HEAD','OPTIONS'])
        
       