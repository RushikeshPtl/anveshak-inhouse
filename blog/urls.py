from django.urls import path
from .views import RoleViewSet,TitleViewSet,EventViewSet,ReviewCommentViewSet,AuthorView,FetchAllBlog,FetchRoleWiseAccount,FetchSortedEvent,PageReadLog
from rest_framework_nested import routers
router = routers.DefaultRouter()

router.register('titles',viewset=TitleViewSet,basename='titles')
title_router = routers.NestedDefaultRouter(router,'titles',lookup='title')
title_router.register('events',viewset=EventViewSet,basename='title-events')
router.register('events',viewset=EventViewSet,basename='events')
event_router = routers.NestedDefaultRouter(router,'events',lookup='event')
event_router.register('comments',viewset=ReviewCommentViewSet,basename='event-comments')
router.register('roles',viewset=RoleViewSet,basename='roles')

urlpatterns = [
    path('author-interface/', AuthorView.as_view(),name='admin'),
    path('fetch-blogs/',FetchAllBlog.as_view(),name='allblog'),
    path('fetch-role-wise-account/',FetchRoleWiseAccount.as_view(),name="fetchrolewiseaccount"),
    path('fetch-sorted-event/',FetchSortedEvent.as_view(),name="fetchsortedevent"),
    path('page-read-logs/',PageReadLog.as_view(),name="pagereadlogs")
    
] + router.urls + title_router.urls + event_router.urls



