from django.contrib.auth.forms import UserCreationForm
from account_management.models import UserProfile


class UserProfileForm(UserCreationForm):
    """Form for creating and updating user profiles"""

    class Meta:
        model = UserProfile
        fields = [
            'email',
            'first_name',
            'last_name',
            'user_type',
            'phone_number',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_order = [
            'email',
            'first_name',
            'last_name',
            'user_type',
            'phone_number',
            'password1',
            'password2',
        ]
        self.order_fields(field_order)
