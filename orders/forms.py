from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field
from crispy_forms.bootstrap import PrependedText
from .models import OrderItem, Order


class OrderForm(forms.Form):
    # define client form fields
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
        # setting the form tag to false is key so that we can control
        # where the form tag element is placed - solves issue with submitting
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('client_name', css_id='client-name-div',
                       css_class='form-group col-md-4 mb-0'),
                Column('client_phone', css_id='client-phone-div',
                       css_class='form-group col-md-4 mb-0'),
                Column('client_email', css_id='client-email-div',
                       css_class='form-group col-md-4 mb-0'),
                # Add a custom HTML div element that will be used by the
                # search_client.js to show suggestions
                Div(css_id="client-suggestions", css_class="dropdown-menu"),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # setting the form tag to false is key so that we can control
        # where the form tag element is placed - solves issue with submitting
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(
                    # Product field
                    Field(
                        'product',
                        css_class='product-dropdown'
                    ),
                    css_class='form-group col-md-9 mb-1 mb-md-2'
                ),
                Column(
                    # Quantity field
                    Field(
                        'quantity',
                        css_class='quantity-field',
                        min=1,
                        value=1,
                    ),
                    css_class='form-group col-md-3 mb-2 mb-md-3'
                ),
            ),
            # Options container/row div
            Row(
                css_class=("options-form-container p-1 p-md-2 bg-light "
                           "text-dark mb-2 mb-md-3 d-none rounded")
            ),
            Row(
                Column(
                    # Base price field
                    PrependedText('base_price', '€', active=True,
                                  css_class='base-price-field'),
                    css_class='form-group col-sm-6 col-md-12 mb-1 mb-md-2'
                ),
                Column(
                    # Discount field
                    PrependedText('discount', '€', active=True,
                                  css_class='discount-field', min=0),
                    css_class='form-group col-sm-6 col-md-12 mb-1 mb-md-2'
                ),
                Column(
                    # Item value field
                    PrependedText('item_value', '€', active=True,
                                  css_class='item-value-field',
                                  readonly=True),
                    css_class='form-group col-12'
                ),
                css_class="row bg-secondary text-white mb-1"
            ),
        )

    # add custom server-side validation for option-values when a product has
    # options as this is set to blank=True in the model so there is no
    # validation in the backend
    # def clean(self):
    #     cleaned_data = super().clean()
    #     product = cleaned_data.get('product')
    #     product_obj = get_object_or_404(Product, product=product)
    #     option_values = cleaned_data.get('option_values')
    #     print(product, option_values)
    #     # if product has options
    #     if product and product.options.exists():
    #         # If the product has options but no option values are selected,
    #         # raise a Validation error
    #         if not option_values:
    #             self.add_error('options',
    #                            'This product requires an option to be selected.'
    #                            )


# Create the order items formset
OrderItemFormSet = forms.modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=1,  # Start with 1 empty form
    can_delete=True,  # Allow deletion of forms
)


# define form for the Orders view
class OrderViewForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status']
        widgets = {
            'order_status': forms.Select(
                attrs={'class': 'form-select'})
        }


# Create the order view formset
OrderViewFormSet = forms.modelformset_factory(Order,
                                              form=OrderViewForm,
                                              extra=0)
