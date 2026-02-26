from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """Form for creating and updating products in the marketplace."""
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'description',
            'price',
            'stock',
            'location',
            'image',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 
                                           'placeholder': 'e.g., 1080p Web Camera'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 
                                                 'rows': 4, 
                                                 'placeholder': 'Describe your product...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control',
                                              'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control',
                                              'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'e.g., Quezon City, Metro Manila'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
