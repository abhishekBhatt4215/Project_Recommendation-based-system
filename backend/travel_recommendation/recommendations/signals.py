from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Traveler


@receiver(post_save, sender=User)
def create_traveler_for_user(sender, instance, created, **kwargs):
    if created:
        # create a Traveler profile for new users if not exists
        Traveler.objects.get_or_create(user=instance)
