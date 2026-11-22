from django import forms
from .models import Store, Product
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class StoreForm(forms.ModelForm):
    # Form for creating a store
    class Meta:
        model = Store
        fields = ['name', 'description', 'logo']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Store name',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Store description',
                'class': 'form-control',
                'rows': 4
            }),
            'logo': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            })

        }


class ProductForm(forms.ModelForm):
    # Form for creating a product
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'qty', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Product name',
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'form-control',
                'min': '0',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Product description',
                'class': 'form-control',
                'rows': 4
            }),
            'qty': forms.NumberInput(attrs={
                'placeholder': '0',
                'class': 'form-control',
                'min': '0'
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            })
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


class SignupForm(UserCreationForm):
    # Form for user signup
    user_type = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('vendor', 'Vendor')],
        widget=forms.RadioSelect()
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")

        return email
