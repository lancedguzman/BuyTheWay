from django import forms
from .models import Product


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
            'price': forms.NumberInput(attrs={'class': 'form-control',
                                              'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control',
                                              'min': '0'}),
            'group_payment': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
            'group_price': forms.NumberInput(attrs={'class': 'form-control',
                                                    'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'rows': 4,
                                                 'placeholder':
                                                 'Describe your product...'}),
            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control-file'}),
        }
