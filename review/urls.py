from django.urls import path
from .views import ReviewerAssignedEventsViewSet,AuthorViewSet,ReviewerCommentsViewSet,AssignReviewer,FetchReviewerEvent,FetchReviewerEventCount,AssignContentWriter,ContentWriterProfileViewSet
from rest_framework_nested import routers
router = routers.DefaultRouter()
router.register('assigned-events',viewset=ReviewerAssignedEventsViewSet,basename='assigned_events')

assigned_event_router = routers.NestedDefaultRouter(router,'assigned-events',lookup='assigned_event')
assigned_event_router.register('comments',viewset=ReviewerCommentsViewSet,basename='assigned-event-comments')

router.register('author',viewset=AuthorViewSet,basename='author')
router.register('assign-content-writer',viewset=AssignContentWriter,basename='assign content-writer')
router.register('content-writer-profile',viewset=ContentWriterProfileViewSet,basename='content-writer-profile')

urlpatterns = [
    path('assign-reviewer/',AssignReviewer.as_view(),name='assignreviewer' ),
    path('fetch-reviewer-event/',FetchReviewerEvent.as_view(),name='fetchreviewerblogs'),
    path('fetch-reviewer-event-count/',FetchReviewerEventCount.as_view(),name='fetchreviewereventcount')

]+router.urls + assigned_event_router.urls