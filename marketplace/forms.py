from django import forms
from .models import Product, Order


class ProductForm(forms.ModelForm):
    """Form for creating and updating products in the marketplace."""
    class Meta:
        model = Product
        fields = [
            'name',
            'location',
            'expected_delivery',
            'category',
            'price',
            'stock',
            'group_payment',
            'group_price',
            'description',
            'image',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder':
                                           'e.g., 1080p Web Camera'}),
            'location': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder':
                                               'e.g., Quezon City'}),
            'expected_delivery': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            # Added min="0.01" to prevent negative numbers in UI
            'price': forms.NumberInput(attrs={'class': 'form-control',
                                              'step': '0.01', 'min': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control',
                                              'min': '0'}),
            'group_payment': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
            # Added min="0.01" to prevent negative numbers in UI
            'group_price': forms.NumberInput(attrs={'class': 'form-control',
                                                    'step': '0.01', 'min': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'rows': 4,
                                                 'placeholder':
                                                 'Describe your product...'}),
            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control-file'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Selling price must be greater than 0.")
        return price

    def clean_group_price(self):
        group_price = self.cleaned_data.get('group_price')
        # Only validate > 0 if a group price is actually provided
        if group_price is not None and group_price <= 0:
            raise forms.ValidationError("Group payment price must be greater than 0.")
        return group_price

    def clean(self):
        cleaned_data = super().clean()
        group_payment = cleaned_data.get('group_payment')
        group_price = cleaned_data.get('group_price')

        # Check if they checked the box but didn't provide a price
        if group_payment and not group_price:
            self.add_error('group_price', 'A group payment price is required if group payments are allowed.')
        
        # If they didn't check the box, silently ignore/clear any group price they might have hacked in
        elif not group_payment and group_price is not None:
            cleaned_data['group_price'] = None

        return cleaned_data