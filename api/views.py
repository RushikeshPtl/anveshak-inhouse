import rest_framework  
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status,viewsets
from rest_framework.authtoken.models import Token
from blog.models import Role
from .serializers import AccountSerializer, SignUpSerializer,UpdateSerializer,AdminSerializer,DocumentSerializer,ChangePasswordSerializer
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account
import uuid
from django.http import HttpResponse
from django.core.mail import send_mail
from . import tasks
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from blog.renderers import CustomRenderer
from blog.permissions import IsAdmin,IsAuthor,IsContentWriter,IsReviewer,IsUser
from .pagination import CustomPageNumberPagination  


class FileView(rest_framework.views.APIView):
  parser_classes = (MultiPartParser,FormParser)

  def post(self, request, *args, **kwargs):
    file_serializer =DocumentSerializer(data=request.data)
    if file_serializer.is_valid():
      file_serializer.save()
      return Response(file_serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([rest_framework.permissions.AllowAny,])  
class SignUpApi(rest_framework.views.APIView):
    def get(self,request):
        return Response({'msg':'Get Request'})
   
    def post(self,request):
        serializer = SignUpSerializer(data=request.data)
        data = {}
        
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "Successfully Registered a new user"
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            
            data['email'] = user.email
            token = Token.objects.get(user=user).key
            data['token'] = token
            
        else:
            data = serializer.errors

        return Response(data)
    
                 
@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None,created=False,**kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_role(sender,instance=None,created=False,**kwargs):
    if created:
        Role.objects.create(account=instance)

@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def send_welcome_mail(sender,instance=None,created=False,**kwargs):
    if created:
        subject = 'welcome to Anveshak_Inhouse'
        message = f'Hi {(instance.first_name, instance.last_name)}, thank you for registering in Anveshak_Inhouse'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email, ]
        send_mail( subject, message, email_from, recipient_list )
        
        
@permission_classes((rest_framework.permissions.AllowAny,))
class ResetPassword(rest_framework.views.APIView):
    def post(self,request,format = "json"):
        try:
            user = Account.objects.filter(email = self.request.data.get("email"))  
            if not user.exists():
                raise AssertionError(f"Invalid Email")
            print("Hello")
            user = user[0]
            user.password_reset = str(uuid.uuid4())
            user.save()
            if tasks.mailSent.delay(user.email, user.password_reset) :
                return Response({"Email sent"})
        
        except (AssertionError) as ex:
                return Response({"Email has not been sent"})

@permission_classes((rest_framework.permissions.AllowAny,))
class NewPassword(rest_framework.views.APIView):
    def post(self,request,format = "json"):
    
        if not self.request.data.get("password_reset_token"):
            raise AssertionError(f"password_reset_token must be provided")
        if not self.request.data.get("confirm_password"):
            raise AssertionError(f"confirm_password must be provided")
        if not self.request.data.get("reconfirm_password"):
            raise AssertionError(f"reconfirm_password must be provided")

        if self.request.data.get("confirm_password") != self.request.data.get("reconfirm_password"):
            raise AssertionError(f"password should be same")
        
        user = Account.objects.filter(password_reset = self.request.data.get("password_reset_token"))

        if not user.exists():
            raise AssertionError(f"Invalid Token")
        
        user = user[0]
        user.password_reset = " "
        user.set_password(self.request.data.get("confirm_password"))
        user.save()
        
        return Response({"Password Reseted Successfully"})


class UpdateAccount(rest_framework.views.APIView):  #Check for authorisations.
    
    def get(self,request,pk):
        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return HttpResponse(status=404)
        serializer = UpdateSerializer(account)
        return Response(serializer.data)
        
    def patch(self,request,pk):
        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return HttpResponse(status=404)

        data=request.data
        serializer = UpdateSerializer(account,data=data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)


class AdminPanel(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    pagination_class=CustomPageNumberPagination
    queryset = Account.objects.all()
    permission_classes = [rest_framework.permissions.IsAdminUser]
    
    def list(self,request):
        serializer = AccountSerializer(self.queryset,many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def partial_update(self, request,pk):
        user = Account.objects.get(pk=pk)
        
        serializer = AdminSerializer(user,data=request.data ,partial=True)
  
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)
    


class UploadView(rest_framework.views.APIView):
  parser_classes = (MultiPartParser, FormParser)

  def post(self, request,pk, *args, **kwargs):
    file_serializer = DocumentSerializer(data=request.data)
    if file_serializer.is_valid():
      file_serializer.save()
      return Response(file_serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = Account 
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user


class GetAllUserView(viewsets.ModelViewSet):
    """
    List of all Users
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    pagination_class=CustomPageNumberPagination
    
    
class AdminAddUser(viewsets.ModelViewSet):
    renderer_classes = [CustomRenderer]
    queryset = Account.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [IsAdmin]
    
@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def send_registration_mail(sender,instance=None,created=False,**kwargs):
    if created:
        new_line='\n'
        subject = f'Hi {instance.first_name} {instance.last_name}!!! WELCOME to ANVESHAK_INHOUSE. Your Account is Created by Admin.'
        message = f'Thank you for registering.{new_line}Your Login Credentials are: {new_line}email={instance.email} {new_line}password={instance._password}.{new_line}Do not share your password with anyone.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email, ]
        send_mail(subject, message, email_from, recipient_list)
   