from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings

# This manager handles creating regular users and superusers
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, role=None, **extra_fields):

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)  # hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role="admin", **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    # Role choices
    
    USER = "user"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (USER, "User"),
        (ADMIN, "Admin")
    ]

    email    = models.EmailField(unique=True)
    role     = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD  = "email"       # login with email instead of username
    REQUIRED_FIELDS = []            # no extra required fields for createsuperuser

    def __str__(self):
        return f"{self.email} ({self.role})"


class UserDetails(models.Model):

    MALE="male"
    FEMALE="female"

    GENDER_CHOICES=[
        (MALE,"male"),
        (FEMALE,"female"),
    ]

    # with ForeignKey a user can have multiple records, hence not used
    user=models.OneToOneField(CustomUser , on_delete=models.CASCADE , related_name="details")

    name=models.CharField(max_length=30)

    profile=models.ImageField( upload_to='profiles/' , blank=True , null=True)

    gender=models.CharField(max_length=10 , choices=GENDER_CHOICES)

    city=models.CharField(max_length=30)

    def __str__(self):
        return self.name