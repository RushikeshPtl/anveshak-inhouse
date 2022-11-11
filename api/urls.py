from django.urls import path
from .views import  UploadView, SignUpApi,ResetPassword,NewPassword,UpdateAccount,AdminPanel
from rest_framework.authtoken import views

urlpatterns = [
    path('signup/', SignUpApi.as_view(),name="signup"),
    path('login/',views.obtain_auth_token),
    path('update/<str:pk>',UpdateAccount.as_view(), name="update"),
    path("reset-password/",ResetPassword.as_view()),
    path("change-password/",NewPassword.as_view()),
    path('upload/<str:pk>', UploadView.as_view(), name='file-upload')
    
]