from django.forms import forms, modelformset_factory
from .models import (Client, Order, OrderItem, OptionValue, FinishOption,
                     Product)


class OrderForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        # Dropdown for existing clients
        queryset=Client.objects.all(),
        # Allow creating new clients
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    new_client_name = forms.CharField(required=False,
                                      widget=forms.TextInput(
                                          attrs={'class': 'form-control'}))
    new_client_phone = forms.CharField(required=False,
                                       widget=forms.TextInput(
                                           attrs={'class': 'form-control'}))
    new_client_email = forms.EmailField(required=False,
                                        widget=forms.EmailInput(
                                            attrs={'class': 'form-control'}))

    class Meta:
        model = Order
        fields = ['client']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'option_values', 'finishes']

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
OrderItemFormSet = modelformset_factory(OrderItem,
                                        form=OrderItemForm,
                                        extra=1)
