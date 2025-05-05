from django.forms import ModelForm
from django import forms
#accessing our models to create forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class StockForm(ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'  # Include all fields from the Stock model   

class UpdateStockForm(ModelForm):
    received_quantity = forms.IntegerField()
    class Meta:
        model = Stock
        fields = '__all__' 

class IssueItemForm(forms.Form):
    produce = forms.ModelChoiceField(queryset=Stock.objects.all(), label="Select Produce")
    quantity_to_sell = forms.DecimalField(
        min_value=0.01,
        label="Quantity to Sell (kgs)",
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ['produce', 'quantity', 'price', 'amount_paid_ugx', 'buyer_name', 'branch']

class ProcurementForm(ModelForm):
    class Meta:
        model = Procurement
        fields =  ['produce', 'tonnage_kgs', 'costUgx', 'dealername', 'branch', 'contact', 'selling_price_ugx'] # Include all fields from the Procurement model

class UserCreation(UserCreationForm):
    class Meta:
        model = Userprofile
        fields = '__all__'
    def save(self, commit=True):
        user = super(UserCreation, self).save(commit=False)
    
        if commit:
            user.is_active = True
            user.is_staff = True
            user.save()
        return user
class CreditSaleForm(forms.ModelForm):
    class Meta:
        model = CreditSale
        fields = ['produce', 'buyer_name', 'national_id', 'tonnage_kgs', 'amount_due_ugx', 'sales_agent', 'due_date']

class CreditPaymentForm(forms.ModelForm):
    class Meta:
        model = CreditPayment
        fields = '__all__' 
    
