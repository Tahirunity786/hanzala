from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, otp, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user, created = self.get_or_create(
            email=self.normalize_email(email),
            otp=otp,
            defaults={'username': username, **extra_fields}
        )

        if not created:
            # Update other fields if the user already exists
            user.username = username
            user.otp = otp
            user.set_password(password)
            user.save(using=self._db)

        return user

    def create_staffuser(self, username, email, otp, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, otp, password, **extra_fields)



class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=150, default='', unique=True)
    otp = models.BigIntegerField(null=True)
    otp_delay = models.TimeField(auto_now=True)
    otp_limit = models.IntegerField(default=1)
    is_active = models.BooleanField(default=False)
    password = models.CharField(max_length=200, default='')
    is_verified = models.BooleanField(default=False)
    # Handling the user is blocked by staff
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] # Email & Password are required by default.
    
    # hook in the New Manager to our Model
    objects = UserManager()