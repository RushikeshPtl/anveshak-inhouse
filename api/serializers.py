from rest_framework import serializers
from .models import Account, Document

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["first_name","last_name","middle_name","email","phone","dob","gender","password","roles"]


class SignUpSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = Account
        fields = ["first_name","last_name","middle_name","email","phone","dob","gender","password","password2"]

        extra_kwargs = {
        'password':{'write_only': True}
        }

    def	save(self):

        user = Account(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            middle_name=self.validated_data['middle_name'],
            email=self.validated_data['email'],
            phone=self.validated_data['phone'],
            dob=self.validated_data['dob'],
            gender=self.validated_data['gender'],
            # is_admin = self.validated_data['is_admin'],
            # is_staff = self.validated_data['is_staff']
            
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user

class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["first_name","last_name","middle_name","email","phone","dob","gender"]



class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        email = serializers.EmailField()
        model = Account
        fields = ["first_name","last_name","is_active","is_staff","is_admin"]

class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields ='__all__'