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
            'store_name',  # Added here
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
            'store_name',  # Added here
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
        self.fields['store_name'].label = 'Store Name' # Optional: Add label
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['birthdate'].label = 'Date of Birth'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        
        self.fields['phone_number'].widget.attrs['placeholder'] = "+639123456789 or 09123456789"
        self.fields['birthdate'].widget.attrs['placeholder'] = "YYYY-MM-DD"
        self.fields['store_name'].widget.attrs['placeholder'] = "Enter store name (Sellers only)"
        
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Because store_name is only required for sellers, ensure the form doesn't 
        # force buyers to fill it out before hitting the model's clean() method.
        self.fields['store_name'].required = False 
        
        self.order_fields(field_order) 
