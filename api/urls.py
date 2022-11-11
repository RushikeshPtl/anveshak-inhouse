from django.urls import path
from .views import  UploadView,SignUpApi,ResetPassword,NewPassword,UpdateAccount,AdminPanel,GetAllUserView,ChangePasswordView,AdminAddUser
from rest_framework.authtoken import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('adminadduser',viewset=AdminAddUser,basename='adminadduser')
router.register('getalluser',viewset=GetAllUserView,basename='getalluser')

urlpatterns = [
    path('signup/', SignUpApi.as_view(),name="signup"),
    path('login/',views.obtain_auth_token),
    path('update/<str:pk>',UpdateAccount.as_view(), name="update"),
    path("forget-password/",ResetPassword.as_view()),         #Changed reset-password to forget-password
    path("reset-password/",NewPassword.as_view()),            #Changed chnage-password to reset-password
    path('upload/<str:pk>', UploadView.as_view(), name='file-upload'),
    path('change-password/<int:pk>',ChangePasswordView.as_view(),name='change-password'),
    
]  + router.urls