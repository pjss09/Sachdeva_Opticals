from django import forms
from .models import (Customer, Purchase, Prescription, Product, Supplier, Inventory, ProductCategory, Bill)
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'date_of_birth', 'gender', 'prescription_date', 'additional_info',
            'sph_left', 'cyl_left', 'axis_left', 'add_left', 'vision_left',
            'sph_right', 'cyl_right', 'axis_right', 'add_right', 'vision_right'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'prescription_date': forms.DateInput(attrs={'type': 'date'}),
            'additional_info': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product_type', 'details', 'date_of_purchase']
        widgets = {
            'date_of_purchase': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.HiddenInput(),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = '__all__'
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'payment_terms': forms.Select(choices=[
                ('COD', 'Cash on Delivery'),
                ('30D', '30 Days Credit'),
                ('60D', '60 Days Credit')
            ])
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = '__all__'
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
        }

class SalesFilterForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data

class BillForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(user=user)
        self.fields['products'].queryset = Product.objects.all()

    class Meta:
        model = Bill
        fields = ['customer', 'products', 'discount', 'payment_method']
        widgets = {
            'products': forms.CheckboxSelectMultiple,
            'payment_method': forms.RadioSelect
        }