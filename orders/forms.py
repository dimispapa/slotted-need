from django import forms
from .models import OrderItem, OptionValue, FinishOption, Product


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


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'option_values', 'finish_options']
        widgets = {
            'product': forms.Select(
                attrs={'class': 'form-control product-dropdown'}),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control'}),
            'option_values': forms.SelectMultiple(
                attrs={'class': 'form-control option-values-dropdown'}),
            'finish_options': forms.SelectMultiple(
                attrs={'class': 'form-control finish-options-dropdown'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate available products as initial rendering
        self.fields['product'].queryset = Product.objects.all()

        # OptionValues and FinishOptions are dynamically updated via JavaScript
        # based on product selection so these fields are rendered as empty
        # initially
        self.fields['option_values'].queryset = OptionValue.objects.none()
        self.fields['finish_options'].queryset = FinishOption.objects.none()


# create a formset object to allow multiple forms in the same order
OrderItemFormSet = forms.modelformset_factory(OrderItem,
                                              form=OrderItemForm,
                                              extra=1)
