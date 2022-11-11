from django.db import models
from django.contrib.auth.models  import AbstractBaseUser,UserManager

# Create your models here.
class Account(AbstractBaseUser):
    gender_choices = [
        ("M","Male"),
        ("F","Female")
    ]
   
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    middle_name = models.CharField(max_length=10, null = True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, null = True)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=1,choices=gender_choices,default="M")
    is_active = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(default=None, null=True)
    password_reset = models.CharField(max_length=50,unique=True,null=True)
    is_admin =  models.BooleanField(default=0)
    is_staff = models.BooleanField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    objects = UserManager()

    class Meta:
        db_table = u'api_account'


class Document(models.Model):
    account = models.OneToOneField(Account,on_delete = models.CASCADE, primary_key=True)
    file = models.FileField(upload_to='Docs/',default='Docs/None/No-doc.pdf')
    img = models.ImageField(upload_to='Images/',default='Images/None/No-img.jpg')

