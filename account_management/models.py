from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator


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

    # Custom fields
    user_type = models.CharField(
        max_length=1,
        choices=USER_CHOICES,
        blank=False,
        null=False,
    )
    
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=13, 
        help_text="Format: +639123456789 or 09123456789"
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
        help_text="Format: YYYY-MM-DD"
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
