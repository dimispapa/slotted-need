from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from .models import OrderItem


class OrderForm(forms.Form):
    client_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',  # Disable browser autocomplete
        'id': 'client_name'
    }))
    client_phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'client_phone'
    }))
    client_email = forms.EmailField(widget=forms.EmailInput(attrs={
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

    # initialisation with a defined form layout
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('client_name', css_class='form-group col-md-4 mb-0'),
                # Add a custom HTML div element that will be used by the
                # search_client.js to show suggestions
                HTML("""
                    <div id="client-suggestions" class="dropdown-menu"></div>
                    """),
                Column('client_phone', css_class='form-group col-md-4 mb-0'),
                Column('client_email', css_class='form-group col-md-4 mb-0'),
            ),
            # Exclude 'deposit' and 'order_value' from automatic layout and
            # manually define position in template at the bottom
        )


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'base_price', 'discount', 'item_value',
                  'quantity', 'option_values', 'finish_options']
        widgets = {
            'product': forms.Select(
                attrs={'class': 'form-control product-dropdown'}),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control quantity-field',
                       'min': 1, 'value': 1}),
            'base_price': forms.NumberInput(
                attrs={'class': 'form-control base-price-field',
                       'readonly': False}),
            'discount': forms.NumberInput(
                attrs={'class': 'form-control discount-field',
                       'min': 0}),
            'item_value': forms.NumberInput(
                attrs={'class': 'form-control',
                       'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('product', css_class='form-group col-md-9'),
                Column('quantity', css_class='form-group col-md-3'),
            ),
            HTML("""
                <div class="container-fluid">
                  <div id="dynamic-options-container-{{ forloop.counter0 }}"
                    class="row">
                  </div>
                </div>
                """),
            Row(
                Column('base_price'),
                Column('discount'),
                Column('item_value'),
            ),
        )


# Create the formset
OrderItemFormSet = forms.modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=1,  # Start with 1 empty form
    can_delete=True,  # Allow deletion of forms
)
