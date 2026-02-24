from django.contrib.auth.forms import UserCreationForm
from account_management.models import UserProfile


class UserProfileForm(UserCreationForm):
    """Form for creating and updating user profiles"""

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
        field_order = [
            
            'first_name',
            'last_name',
            'user_type',
            'birthdate',
            'email',
            'phone_number',
            'password1',
            'password2',
        ]
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['user_type'].label = 'User Type'
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['birthdate'].label = 'Date of Birth'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        self.fields['phone_number'].widget.attrs['placeholder'] = "+639123456789 or 09123456789"
        self.fields['birthdate'].widget.attrs['placeholder'] = "YYYY-MM-DD"
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.order_fields(field_order)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Handle store_name from POST data (added dynamically by JavaScript)
        if 'store_name' in self.data:
            user.store_name = self.data.get('store_name', '')
        if commit:
            user.save()
        return user
