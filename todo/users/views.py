from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import authentication
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from django.core.mail import send_mail
from django.contrib.auth.models import update_last_login
from django_rest_passwordreset.signals import reset_password_token_created
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver

from social_django.utils import psa

import uuid

from todo import config
from .models import User, Profile, Task
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, ProfileSerializer, TaskSerializer

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)

class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)

    def create(self, request): 
        if request.user.id: 
            Profile.objects.create(user=request.user).save()
        return super().create(request)    

class ProfileRetrieveView(APIView): 
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        if profile is not None: 
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        else: 
            return Response(False)

class TaskView(APIView): 
    def get(self, request): 
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request): 
        if "id" in request.data and "description" in request.data and "priority" in request.data: 
            task = Task.objects.get(id=request.data["id"])
            if task is None: 
                Task.objects.create(description=request.data["description"])
            else: 
                task.description = request.data["description"]
                task.priority = request.data["priority"]
                task.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response()

@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
@psa()
def third_party_auth(request, backend):
    user = None
    if "userSetup" in request.data:
        userSetup = request.data["userSetup"]
        token = request.data["token"]
        user = request.backend.do_auth(request.data["token"])
        profile = Profile.objects.get(user=user)
        if profile.email_verified == False: 
            profile.email_verified = True
            profile.save()
    if user == None: 
        return Response(status=status.HTTP_403_FORBIDDEN)
    token = Token.objects.get(user=user)
    output = {}
    output["auth_token"] = token.key
    return Response(output)

@api_view(["POST"])
def deactivate_account(request): 
    user: User = request.user
    user.is_active = False
    user.save()
    return Response(status=status.HTTP_202_ACCEPTED)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'first_name': reset_password_token.user.first_name,
        'unsubscribe': "https://todo.com/settings", 
        'reset_password_url': "{}/reset-password/{}".format(config.UI_ENDPOINT, reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
    send_mail(
        subject="todo", 
        message=email_plaintext_message,
        html_message=email_html_message, 
        from_email="willemdrescher@yahoo.com", 
        recipient_list=[reset_password_token.user.email]
    )
