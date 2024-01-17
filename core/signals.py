from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a user profile when a new user is created.

    Args:
        sender: The sender model class.
        instance: The User instance being saved.
        created (bool): A boolean indicating whether the instance was created.

    Returns:
        None
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the user profile when the associated User instance is saved.

    Args:
        sender: The sender model class.
        instance: The User instance being saved.

    Returns:
        None
    """
    instance.profile.save()
