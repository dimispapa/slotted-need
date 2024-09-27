from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field
from crispy_forms.bootstrap import PrependedText
from .models import OrderItem, Order, Product, OptionValue


class OrderForm(forms.Form):
    # define client form fields
    client_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off',  # Disable browser autocomplete
        'id': 'client_name'
    }), required=True)
    client_phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'client_phone'
    }), required=True)
    client_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'id': 'client_email'
    }), required=True)

    # read-only deposit and order_value fields
    order_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'order_value'
        }),
        required=True
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

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        widget=forms.Select()
    )

    # Define 'quantity' as a form-only field
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'min': '1'}),
        required=True,
    )

    base_price = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput()
    )

    item_value = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput()
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'base_price', 'discount', 'item_value',
                  'option_values']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ***** FIELD LEVEL VALIDATION *********
        # Dynamically set the queryset for option_values based on the
        # selected product and handle errors to data

        # Handle when a product is in the new form data
        if 'product' in self.data:

            try:
                product_id = int(self.data.get('product'))
                product = Product.objects.get(id=product_id)
                self.fields['option_values'
                            ].queryset = OptionValue.objects.filter(
                    option__product=product)

            # Handle cases when product does not exist or
            # ID cannot be converted to int
            except (ValueError, TypeError, Product.DoesNotExist):
                self.fields['option_values'
                            ].queryset = OptionValue.objects.none()

        # Handle an existing order item instance
        elif self.instance.pk and self.instance.product:
            product = self.instance.product
            self.fields['option_values'].queryset = OptionValue.objects.filter(
                option__product=product)

        # Handle when a product is not selected
        else:
            self.fields['option_values'].queryset = OptionValue.objects.none()

        # *** FORM LAYOUT DESIGN WITH CRISPY-DJANGO FORM-HELPER ***
        # Initialise the form helper to design the layout of the form
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
                        css_class='quantity-field'
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

    # add custom server-side validation for option-values to ensure
    # data integrity if client-side validation is bypassed
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')

        if not product:
            # raise validation error as an order item must have a product
            if not self.has_error('product'):
                self.add_error('product', 'This field is required.')

        return cleaned_data


# Create the order items formset
OrderItemFormSet = forms.inlineformset_factory(
    parent_model=Order,
    model=OrderItem,
    form=OrderItemForm,
    fields=['product', 'base_price', 'discount', 'item_value', 'quantity',
            'option_values'],
    extra=1,  # Start with 1 empty form
    can_delete=False,  # Deletion only on the front-end
)


# define form for the Orders view
class OrderViewForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['paid']
        widgets = {
            'paid': forms.Select(
                attrs={'class':
                       'form-select form-select-sm paid-status-select '
                       'fw-bolder text-wrap'
                       })
        }


# define form for the OrdersItem view
class OrderItemViewForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['item_status']
        widgets = {
            'item_status': forms.Select(
                attrs={'class':
                       'form-select form-select-sm item-status-select '
                       'fw-bolder text-wrap'})
        }


# Create the order view formset
OrderViewFormSet = forms.inlineformset_factory(
    parent_model=Order,
    model=OrderItem,
    form=OrderItemViewForm,
    fields=('item_status',),
    extra=0,
    can_delete=True
)
