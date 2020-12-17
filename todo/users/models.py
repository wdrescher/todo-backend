import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from todo import config
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        # email_token = EmailToken.objects.create(user=instance)
        # user = instance

        # context = {
        #     'first_name': user.first_name,
        #     'unsubscribe': "https://befounders.com/settings", 
        #     'verify_email_url': "{}/verify-email/{}".format(config.UI_ENDPOINT, email_token.key)
        # }

        # # render email text
        # email_html_message = render_to_string('email/user_verify_email.html', context)
        # email_plaintext_message = render_to_string('email/user_verify_email.txt', context)

        # msg = EmailMultiAlternatives(
        #     # title:
        #     "Be Founders: Verify Email",
        #     # message:
        #     email_plaintext_message,
        #     # from:
        #     "Be Founders <no-reply@befounders.com>",
        #     # to:
        #     [user.email]
        # )
        # msg.attach_alternative(email_html_message, "text/html")
        # msg.send()


class Profile(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self): 
        return self.user.email    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    def __str__(self):
        return self.username

