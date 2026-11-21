from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator  # Add MaxValueValidator if needed
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

 
class Survey(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=100, default="Movie Survey") # Good to have a survey title
    movie = models.CharField(max_length=100)  # Increased length for longer movie titles
    
    # Rating out of 5 or 10, adding validators is recommended
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    movie_image = models.ImageField(
        upload_to='survey_movies/',
        blank=True,
        null=True
    )
    description = models.TextField(max_length=500) # TextField or larger char length for descriptions

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_by = models.ForeignKey(
        'users.CustomUser',  
        on_delete=models.CASCADE,
        related_name='created_surveys'
    )

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie} Survey ({self.status})"

    class Meta:
        ordering = ['-created_at']


class SurveyQuestion(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='survey_questions'
    )

    question_text = models.CharField(max_length=255) 
    choice_1 = models.CharField(max_length=255)
    choice_2 = models.CharField(max_length=255)
    choice_3 = models.CharField(max_length=255)
    choice_4 = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return f"Q{self.order}: {self.question_text}"

    class Meta:
        ordering = ['order']
        unique_together = ('survey', 'order') 


class UserSurveyResponse(models.Model):
    

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='survey_responses'
    )
    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    selected_choice = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    has_attended = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_user_question_response'
            )
        ]

    def __str__(self):
        status = "Attended" if self.has_attended else "Not Attended"
        return f"{self.user} - {self.question} ({status})"

    @property
    def selected_choice_text(self):
        """Returns the actual choice text from SurveyQuestion if selected."""
        if not self.selected_choice:
            return None
        return getattr(self.question, self.selected_choice, None)