from django import forms
from .models import OrderItem


class OrderForm(forms.Form):
    client_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',  # Disable browser autocomplete
        'id': 'client_name'
    }))
    client_phone = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={
                                       'class': 'form-control',
                                       'id': 'client_phone'
                                   }))
    client_email = forms.EmailField(required=False,
                                    widget=forms.EmailInput(attrs={
                                        'class': 'form-control',
                                        'id': 'client_email'
                                    }))

    # read-only deposit and order_value fields
    order_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'order_value'
        }),
        required=False,  # Optional as we populate it dynamically
    )
    deposit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'order_deposit'
        }),
        required=False,  # Optional as not all orders pay deposit
    )


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'base_price', 'discount', 'item_value',
                  'quantity', 'option_values', 'finish_options']
        widgets = {
            'product': forms.Select(
                attrs={'class': 'form-control product-dropdown'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control',
                                                   'readonly': False}),
            'discount': forms.NumberInput(attrs={'class':
                                                 'form-control discount-field',
                                                 'min': 0}),
            'item_value': forms.NumberInput(attrs={'class': 'form-control',
                                                   'readonly': True}),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control quantity-field',
                       'min': 1, 'value': 1}),
            'option_values': forms.SelectMultiple(
                attrs={'class': 'form-control option-values-dropdown'}),
            'finish_options': forms.SelectMultiple(
                attrs={'class': 'form-control finish-options-dropdown'})
        }


# Create the formset
OrderItemFormSet = forms.modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=1,  # Start with 1 empty form
    can_delete=True,  # Allow deletion of forms
)
