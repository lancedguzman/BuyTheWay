from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.contrib.auth.models import BaseUserManager


class UserProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class UserProfile(AbstractUser):
    """Model representing a user profile with 
    their personal information
    """
    # Gender Choices
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    USER_CHOICES = [
        ('B', 'Buyer'),
        ('S', 'Seller'),
    ]

    # Philippine Phone Number Validator (+639XXXXXXXXX or 09XXXXXXXXX)
    phone_regex = RegexValidator(
        regex=r'^(?:\+63|0)9\d{9}$',
        message="Phone number must be entered in the format: '+639XXXXXXXXX' or '09XXXXXXXXX'."
    )

    # Use email as username
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserProfileManager()

    # Custom fields
    user_type = models.CharField(
        max_length=1,
        choices=USER_CHOICES,
        blank=False,
        null=False,
    )
    
    store_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=13, 
    )
    
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True, 
        null=True
    )
    
    birthdate = models.DateField(
        blank=True, 
        null=True, 
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        blank=True,
        null=True,
        help_text="Only .png and .jpg formats are allowed."
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
