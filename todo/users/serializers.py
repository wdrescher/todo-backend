from rest_framework import serializers
from .models import User, Profile, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class CreateUserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}

class ProfileSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Profile
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Task
        fields = "__all__"





