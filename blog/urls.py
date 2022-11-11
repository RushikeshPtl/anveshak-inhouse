from django.urls import path
from .views import RoleViewSet,TitleViewSet,EventViewSet,AuthorView,FetchAllBlog,FetchRoleWiseAccount,FetchSortedEvent,PageReadLog,UsersRoleWise,EventsTitleWise
from rest_framework_nested import routers
router = routers.DefaultRouter()

router.register('titles',viewset=TitleViewSet,basename='titles')
title_router = routers.NestedDefaultRouter(router,'titles',lookup='title')
title_router.register('events',viewset=EventViewSet,basename='title-events')
router.register('events',viewset=EventViewSet,basename='events')
# event_router = routers.NestedDefaultRouter(router,'events',lookup='event')
router.register('roles',viewset=RoleViewSet,basename='roles')

urlpatterns = [
    path('author-interface/', AuthorView.as_view(),name='admin'),
    path('fetch-blogs/',FetchAllBlog.as_view(),name='allblog'),
    path('fetch-role-wise-account/',FetchRoleWiseAccount.as_view(),name="fetchrolewiseaccount"),
    path('fetch-sorted-event/',FetchSortedEvent.as_view(),name="fetchsortedevent"),
    path('page-read-logs/',PageReadLog.as_view(),name="pagereadlogs"),
    path('event-title-wise/',EventsTitleWise.as_view(),name='events_title_wise'),
    path('rolewise-user/',UsersRoleWise.as_view(),name='rolewise'),

] + router.urls + title_router.urls 



