from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div
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
                Column('client_phone', css_class='form-group col-md-4 mb-0'),
                Column('client_email', css_class='form-group col-md-4 mb-0'),
                # Add a custom HTML div element that will be used by the
                # search_client.js to show suggestions
                Div(css_id="client-suggestions",
                    css_class="dropdown-menu"),
                css_class='client-form-container'
            ),
            # Exclude 'deposit' and 'order_value' from automatic layout and
            # manually define position in template at the bottom
        )


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'base_price', 'discount', 'item_value',
                  'quantity']
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
                Column(
                    'product',
                    css_class='form-group col-md-9 mb-1 mb-md-2'),
                Column(
                    'quantity',
                    css_class='form-group col-md-3 mb-2 mb-md-3'),
            ),
            HTML("""
                <div id="options-form-{{ forloop.counter0 }}-container"
                class="row p-1 p-md-2 bg-light text-dark mb-1 d-none rounded">
                </div>
                """),
            Row(
                Column(
                    HTML("""
                <label for="id_form-{{ forloop.counter0 }}-base_price"
                class="form-label requiredField">
                    Base price<span class="asteriskField">*</span>
                </label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text">€</span>
                    </div>
                    <input type="number"
                    name="form-{{ forloop.counter0 }}-base_price"
                    class="form-control base-price-field" step="0.01"
                    id="id_form-{{ forloop.counter0 }}-base_price">
                </div>
                """),
                    css_class='col-sm-6 col-md-12 mb-1 mb-md-2'
                ),
                Column(
                    HTML("""
                <label for="id_form-{{ forloop.counter0 }}-discount"
                class="form-label requiredField">
                    Discount
                </label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text">€</span>
                    </div>
                    <input type="number"
                    name="form-{{ forloop.counter0 }}-discount"
                    class="form-control discount-field" step="0.01"
                    id="id_form-{{ forloop.counter0 }}-discount">
                </div>
                """),
                    css_class='col-sm-6 col-md-12 mb-1 mb-md-2'
                ),
                Column(
                    HTML("""
                <label for="id_form-{{ forloop.counter0 }}-item_value"
                class="form-label requiredField">
                    Item value<span class="asteriskField">*</span>
                </label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text">€</span>
                    </div>
                    <input type="number"
                    name="form-{{ forloop.counter0 }}-item_value"
                    class="form-control" step="0.01"
                    id="id_form-{{ forloop.counter0 }}-item_value">
                </div>
                """),
                    css_class='col-12'
                ),
                css_class="row bg-secondary text-white mb-1"
            ),
        )


# Create the formset
OrderItemFormSet = forms.modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=1,  # Start with 1 empty form
    can_delete=True,  # Allow deletion of forms
)
