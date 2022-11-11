from rest_framework import serializers
from .models import Account, Document

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["first_name","last_name","middle_name","email","phone","dob","gender","password","roles"]  #Changes in fields(password should not be visible.)


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
        

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=30)
    password = serializers.CharField(required=True, max_length=30)
    confirmed_password = serializers.CharField(required=True, max_length=30)

    def validate(self, data):
        if not self.context['request'].user.check_password(data.get('old_password')):
            raise serializers.ValidationError({'old_password': 'Wrong password.'})

        if data.get('confirmed_password') != data.get('password'):
            raise serializers.ValidationError({'password': 'Password must be confirmed correctly.'})

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    @property
    def data(self):
        return {'Success': 'Password changed Successfully'}