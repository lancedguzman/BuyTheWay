from django.contrib.auth.forms import UserCreationForm
from django import forms
from account_management.models import UserProfile
from marketplace.models import Store


class UserProfileForm(UserCreationForm):
    """Form for creating user profiles with optional store creation."""

    store_name = forms.CharField(
        max_length=255,
        required=False,
        label="Store Name"
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'user_type',
            'birthdate',
            'email',
            'phone_number',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Order all fields properly (including passwords + store_name)
        self.order_fields([
            'first_name',
            'last_name',
            'user_type',
            'birthdate',
            'store_name',
            'email',
            'phone_number',
            'password1',
            'password2',
        ])

        # Labels
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['user_type'].label = 'User Type'
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['birthdate'].label = 'Date of Birth'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

        # Placeholders
        self.fields['phone_number'].widget.attrs['placeholder'] = "+639123456789 or 09123456789"
        self.fields['birthdate'].widget.attrs['placeholder'] = "YYYY-MM-DD"

        # Remove default help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        store_name = cleaned_data.get('store_name')

        # Require store name only for sellers
        if user_type == 'S' and not store_name:
            self.add_error('store_name', 'Store name is required for sellers.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Create Store only if seller
        if commit and user.user_type == 'S':
            store_name = self.cleaned_data.get('store_name')

            if store_name:
                Store.objects.create(
                    name=store_name,
                    description=f"Welcome to {store_name}!",
                    rating=0,
                    seller=user
                )

        return user
