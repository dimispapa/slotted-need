from django import forms
from .models import OrderItem


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'option_values', 'finishes']
