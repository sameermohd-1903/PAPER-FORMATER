from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Teacher
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'username', 'email', 'department', 'phone_number', 'date_joined']
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include username and password.')
        return data