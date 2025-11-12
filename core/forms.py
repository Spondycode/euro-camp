from django import forms
from .models import Campsite, Product


class CampsiteForm(forms.ModelForm):
    image = forms.FileField(
        required=False,
        label="Primary Image",
        help_text="Upload a campsite image (optional)",
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
        })
    )
    
    class Meta:
        model = Campsite
        fields = ['name', 'town', 'description', 'map_location', 'website', 'phone_number', 'country']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes to form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            field.widget.attrs['placeholder'] = field.label


class ProductForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label="Product Image",
        help_text="Upload a product image (optional)",
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
        })
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'image_url', 'amazon_link', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        help_texts = {
            'image_url': 'Externally hosted image URL (e.g., ImageKit). Leave blank if uploading an image file above.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes to form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['placeholder'] = field.label
