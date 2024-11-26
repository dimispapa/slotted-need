import re
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q, Prefetch
from rest_framework import viewsets, permissions, status, response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from slotted_need.views import BaseLoginRequiredView
from .models import Client, Order, OrderItem, ComponentFinish
from products.models import (Product, Option, OptionValue, FinishOption,
                             ProductComponent, Component, Finish)
from .forms import OrderForm, OrderItemFormSet
from .filters import OrderItemFilter, OrderFilter
from .serializers import OrderItemSerializer, OrderSerializer


@require_POST
# API view to check for client and return matches if any
def check_client(request):
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')
        client_email = request.POST.get('client_email')

        # Check for an exact match
        exact_match = Client.objects.filter(
            client_name__iexact=client_name,
            client_phone__iexact=client_phone,
            client_email__iexact=client_email
        ).first()

        if exact_match:
            return JsonResponse({'exact_match': {
                'id': exact_match.id,
            }})

        # Check for partial match (name + phone or email)
        partial_match = Client.objects.filter(
            Q(client_name__iexact=client_name) &
            (Q(client_phone__iexact=client_phone) |
             Q(client_email__iexact=client_email))
        ).first()

        if partial_match:
            return JsonResponse({'partial_match': {
                'id': partial_match.id,
                'name': partial_match.client_name,
                'phone': partial_match.client_phone,
                'email': partial_match.client_email
            }})

        # No match found
        return JsonResponse({'exact_match': False, 'partial_match': False})


# Function to handle client creation
def get_update_create_client(action, client_id, cleaned_data):
    # If the user is updating the client details
    if action == 'update_client' and client_id:
        client = Client.objects.get(id=client_id)
        # Update the client's details with the new form data
        client.client_name = cleaned_data[
            'client_name']
        client.client_phone = cleaned_data[
            'client_phone']
        client.client_email = cleaned_data[
            'client_email']
        client.save()

    elif action == 'use_existing' and client_id:
        # Use existing client without updating details
        client = Client.objects.get(id=client_id)

    else:
        # Create new client if no client ID or action is passed
        client = Client.objects.create(
            client_name=cleaned_data['client_name'],
            client_phone=cleaned_data['client_phone'],
            client_email=cleaned_data['client_email']
        )

    return client


# View to handle the create order form
@login_required
def create_order(request):
    if request.method == 'POST':

        # pass the post request to the form and formset objects
        order_form = OrderForm(data=request.POST)
        # Initialize the formset with the Order instance (not yet saved)
        order_item_formset = OrderItemFormSet(data=request.POST,
                                              instance=Order())

        # Check if the user has confirmed using the existing client
        client_action = request.POST.get('client_action')
        client_id = request.POST.get('client_id')

        # validation of forms and formset fields ensuring no errors
        if order_form.is_valid() and order_item_formset.is_valid():
            try:
                # use transaction context manager to ensure operations to roll
                # back in case of failure in any one operation
                # - ensure data integrity
                with transaction.atomic():
                    # call function to get, update or create client
                    client = get_update_create_client(client_action,
                                                      client_id,
                                                      order_form.cleaned_data)

                    # Capture calculated totals from the form
                    order_value = order_form.cleaned_data.get('order_value', 0)
                    deposit = order_form.cleaned_data['deposit']

                    # proceed to create order object
                    order = Order.objects.create(
                        client=client,
                        order_value=order_value,
                        deposit=deposit
                    )

                    # Now bind the formset to the saved Order instance
                    order_item_formset = OrderItemFormSet(
                        request.POST, instance=order)

                    # Validate the formset again with the correct instance
                    if order_item_formset.is_valid():

                        # process each form in the formset
                        # to save the order items
                        for form in order_item_formset:
                            # Get the quantity from the form
                            quantity = form.cleaned_data.get('quantity', 1)
                            # Save original OrderItem instance without commit
                            # to process the remainder options/finishes fields
                            order_item = form.save(commit=False)
                            order_item.order = order
                            order_item.save()
                            form.save_m2m()
                            # Get the form index
                            form_index = form.prefix.split('-')[1]
                            # Process option values
                            process_option_values(request,
                                                  form_index,
                                                  order_item)
                            # Process component finishes
                            process_component_finishes(request,
                                                       form_index,
                                                       order_item)
                            # Process option finishes
                            process_option_finishes(request,
                                                    form_index,
                                                    order_item)
                            # Create additional order items instances
                            # based on quantity with same configurations
                            for _ in range(quantity - 1):
                                copy_order_item(order_item)

                        # notify user with success message
                        messages.success(request,
                                         'Order created successfully!')

                        # Redirect to the same page to avoid form resubmission
                        return redirect('create_order')

                    else:
                        # If formset is invalid after binding to the
                        # saved Order, show errors
                        messages.error(request,
                                       'Please correct the errors in the order'
                                       ' items.')

            # catch any other errors as validation errors
            except ValidationError as e:
                messages.error(request,
                               f"There was an error processing the order: {e}")

        # If the forms are not valid
        else:
            # display an error message
            messages.error(request, 'Please correct the errors below.')

        # If the form or formset is invalid, re-render the page with errors
        return render(request, 'orders/create_order.html', {
            'order_form': order_form,
            'order_item_formset': order_item_formset,
        })

    # if a GET request simply start a new form
    else:
        order_form = OrderForm()
        order_item_formset = OrderItemFormSet(
            queryset=OrderItem.objects.none())

        # render the template with form and formset context passed
        return render(request, 'orders/create_order.html', {
            'order_form': order_form,
            'order_item_formset': order_item_formset,
        })


# *** HELPER FUNCTIONS ***
def process_option_values(request, form_index, order_item):
    # Define field naming pattern
    option_field_pattern = re.compile(
        rf'^items-{form_index}-option_\d+$')

    # Get option field names
    option_field_names = [
        key for key in request.POST
        if option_field_pattern.match(key)]

    # Initialise emtpy list of option values
    selected_option_value_ids = []

    # Loop through field names
    for field_name in option_field_names:
        # Extract the option_id
        option_id = field_name.split('-option_')[1]
        # Get the selected values for this option
        selected_values = request.POST.getlist(field_name)
        # Validate and collect the selected OptionValue IDs
        for value_id in selected_values:
            # Validate that the OptionValue exists and
            # is associated with the Option
            if not OptionValue.objects.filter(id=value_id,
                                              option_id=option_id).exists():
                raise ValidationError(
                    f"Invalid option value selected: {value_id}")
            selected_option_value_ids.append(value_id)

    # Associate option values with the order item
    order_item.option_values.set(selected_option_value_ids)


def process_component_finishes(request, form_index, order_item):
    # Define field naming pattern
    comp_finish_field_pattern = re.compile(
        rf'^items-{form_index}-component_finish-\d+$')
    # Get component finish fields
    comp_finish_field_names = [key for key in request.POST
                               if comp_finish_field_pattern.match(key)]

    for field_name in comp_finish_field_names:
        # Extract the component_id
        component_id = field_name.split('-component_finish-')[1]
        finish_option_id = request.POST.get(field_name)

        # Skip this field if no finish option is selected
        if not finish_option_id:
            continue

        # Validate the Component
        if not Component.objects.filter(id=component_id).exists():
            raise ValidationError(
                f"Invalid component selected: {component_id}")

        # Validate the FinishOption
        if not FinishOption.objects.filter(id=finish_option_id).exists():
            raise ValidationError(
                f"Invalid finish option selected: "
                f"{finish_option_id}")

        component = Component.objects.get(id=component_id)
        finish_option = FinishOption.objects.get(id=finish_option_id)

        # Associate the finish option with the component and order item
        order_item.item_component_finishes.create(
            component=component,
            finish_option=finish_option
        )


def process_option_finishes(request, form_index, order_item):
    # get selected OptionValue ids
    selected_option_value_ids = order_item.option_values.values_list(
        'id', flat=True)
    # loop through OptionValue ids
    for option_value_id in selected_option_value_ids:
        # Find ProductComponents associated with this OptionValue
        product_components = ProductComponent.objects.filter(
            product=order_item.product,
            option_value_id=option_value_id
        )

        # loop through relevant product components
        for pc in product_components:
            component = pc.component
            # Build field name
            field_name = (f'items-{form_index}-option_finish_'
                          f'component-{component.id}')
            finish_option_id = request.POST.get(field_name)

            # Skip if no finish option is selected
            if not finish_option_id:
                continue

            # Validate the FinishOption
            if not FinishOption.objects.filter(id=finish_option_id).exists():
                raise ValidationError(
                    f"Invalid finish option selected: "
                    f"{finish_option_id}")

            finish_option = FinishOption.objects.get(id=finish_option_id)

            # Associate the finish option with the component and order item
            order_item.item_component_finishes.create(
                component=component,
                finish_option=finish_option
            )


def copy_order_item(order_item):
    """
    Creates an instance copy of the given OrderItem with the same
    option_values and ComponentFinishes.
    """
    order_item_copy = OrderItem.objects.create(
        order=order_item.order,
        product=order_item.product,
        base_price=order_item.base_price,
        discount=order_item.discount,
        item_value=order_item.item_value,
    )
    # set the same option values
    order_item_copy.option_values.set(
        order_item.option_values.all())
    # Duplicate ComponentFinishes
    for icf in order_item.item_component_finishes.\
            all():
        ComponentFinish.objects.create(
            order_item=order_item_copy,
            component=icf.component,
            finish_option=icf.finish_option,
        )
    return order_item_copy


# *** ORDER LIST VIEW ***
# API view to get the products on initial load of order form
@login_required
def get_products(request):

    # handle get request by returning product data
    if request.method == 'GET':

        # fetch all product objects and compile a json response
        products = Product.objects.all()
        product_data = [{'id': product.id, 'name': product.name}
                        for product in products]
        return JsonResponse({'products': product_data})

    # If not a GET request, return a method not allowed response
    return JsonResponse({'error': 'POST method not allowed'}, status=405)


# API view to the the product data of the selected product in form
@login_required
@require_GET
def get_product_data(request, product_id):

    # handle get request by returning product data
    if request.method == 'GET':

        # Use get_object_or_404 to retrieve the product,
        # or return a 404 if not found
        product = get_object_or_404(Product, id=product_id)

        # Get the options related to the product,
        # but don't raise a 404 as they are optional
        options = Option.objects.filter(product=product)
        options_data = []
        for option in options:
            # Use filter instead of get_list_or_404 to avoid raising
            # a 404 when no option values exist as they are optional
            option_values = OptionValue.objects.filter(option=option)
            option_values_data = [{'id': ov.id, 'value': ov.value}
                                  for ov in option_values]
            options_data.append({
                'id': option.id,
                'name': option.name,
                'option_values': option_values_data
            })

        # Get the finishes related to the product (ManyToManyField)
        # and their options. Returns empty list if not found
        finishes = product.finishes.all()
        finishes_data = []
        for finish in finishes:
            # use filter to retrieve finish options,
            # without raising 404 as they are optional
            finish_options = FinishOption.objects.filter(finish=finish)
            finish_options_data = [{'id': fo.id, 'name': fo.name}
                                   for fo in finish_options]
            finishes_data.append({
                'id': finish.id,
                'name': finish.name,
                'finish_options': finish_options_data
            })

        # Get the components of the product and their associated finishes
        # Filter components that are not associated with
        # any OptionValue and filter for the product through ProductComponent
        components_without_options = Component.objects.filter(
            productcomponent__product=product
        ).annotate(
            option_value_count=Count('productcomponent__option_value')
        ).filter(option_value_count=0)

        # initialise empty component finishes data list
        comp_finish_data = []

        for component in components_without_options:
            # retrieve finishes of component
            finishes = component.finishes.all()

            for finish in finishes:
                # use filter to retrieve finish options,
                # without raising 404 as they are optional
                finish_options = FinishOption.objects.filter(finish=finish)
                finish_options_data = [{'id': fo.id, 'name': fo.name}
                                       for fo in finish_options]
                comp_finish_data.append({
                    'id': finish.id,
                    'name': finish.name,
                    'options': finish_options_data,
                    'component_id': component.id,
                    'component_name': component.name
                })

        # Return the data as JSON
        return JsonResponse({
            'product': product.name,
            'base_price': product.base_price,
            'options': options_data,
            'finishes': finishes_data,
            'component_finishes': comp_finish_data
        })

    # If not a GET request, return a method not allowed response
    return JsonResponse({'error': 'POST method not allowed'}, status=405)


# API function to handle the finish options
# based on the product options selected (associated with components)
@login_required
@require_GET
def get_finishes(request, product_id, option_value_id):

    # handle get request by returning product finishes data
    if request.method == 'GET':

        # get the option_value object and
        # its associated product_component tables
        option_value = get_object_or_404(OptionValue, id=option_value_id)

        # Filter ProductComponent by both product_id and option_value_id
        product_components = ProductComponent.objects.filter(
            product_id=product_id,
            option_value=option_value
        )

        # extract the relevant component in the product_component linking table
        components = [c.component for c in product_components]
        component_finishes = []
        # loop through the components and extract the finish options
        for component in components:
            for finish in component.finishes.all():

                finish_options = FinishOption.objects.filter(finish=finish)
                finish_options_data = [{'id': fo.id, 'name': fo.name}
                                       for fo in finish_options]

                component_finishes.append({
                    'component_id': component.id,
                    'id': finish.id,
                    'name': finish.name,
                    'finish_options': finish_options_data
                })

        # Return the data as JSON
        return JsonResponse({
            'component_finishes': component_finishes
        })

    # If not a GET request, return a method not allowed response
    return JsonResponse({'error': 'POST method not allowed'}, status=405)


# API function to deal with the search client query request
@login_required
@require_GET
def search_clients(request):

    # handle get request by returning product finishes data
    if request.method == 'GET':

        # get query path parameter from request url
        query = request.GET.get('q', '')
        if query:
            # filter the client objects based on client name,
            # limit to 10 results
            clients = Client.objects.filter(client_name__icontains=query)[:10]
            # create client data using list comprehension
            client_data = [
                {'name': client.client_name,
                 'phone': client.client_phone,
                 'email': client.client_email}
                for client in clients
            ]
            return JsonResponse({'clients': client_data})
        return JsonResponse({'clients': []})

    # If not a GET request, return a method not allowed response
    return JsonResponse({'error': 'POST method not allowed'}, status=405)


# define pagination class
class Pagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # Maps to 'page_size' from DataTables
    max_page_size = 100  # Limit maximum page size


# define viewset that feeds the order_items API
class OrderItemViewSet(viewsets.ModelViewSet, LoginRequiredMixin):
    """
    A ViewSet for viewing and editing OrderItem instances.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = OrderItemFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter,
                       filters.SearchFilter]
    ordering_fields = [
        'id',
        'order__id',
        'order__client__client_name',
        'order__created_on',
        'product__name',
        'product_finish__name',
        'item_value',
        'item_status',
        'priority_level',
        'order__paid',
        'completed'
    ]
    ordering = ['-priority_level']  # Default ordering

    # Define fetching queryset process
    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset()

        # Get query parameters if any
        order_id = self.request.query_params.get('order_id', None)
        filter_type = self.request.query_params.get('filter_type', None)

        # If 'order_id' is provided, filter the queryset
        if order_id:
            queryset = queryset.filter(order__id=order_id)

        # If filter type is provided, filter the queryset
        if filter_type == 'home_dashboard':
            # Apply specific filters:
            # Fully Paid but Not Started OR Delivered but Not Paid
            queryset = queryset.filter(
                Q(order__paid=2, item_status=1) |
                Q(order__paid=1, item_status=4)
            )

        # Optimize related objects with related objects for filtered queryset
        queryset = OrderItem.objects.select_related(
            'order',
            'order__client',
            'product',
            'product_finish'
        ).prefetch_related(
            'option_values',
            Prefetch(
                'item_component_finishes',
                queryset=ComponentFinish.objects.select_related(
                    'finish_option', 'component')
            ),
            Prefetch(
                'product__components',
                queryset=Component.objects.all()
            ),
            Prefetch(
                'product_finish__finish_option',
                queryset=FinishOption.objects.all()
            )
        ).all().order_by('-id')

        # Return the filtered or full queryset
        return queryset

    # Define deletion (destroy) process
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Store instance id before deletion
        id = instance.id
        # Delete the instance
        self.perform_destroy(instance)

        # Return response
        return response.Response(
            {'success': True,
             'message': f'Order item {id} deleted successfully.'},
            status=status.HTTP_200_OK
        )


class OrderItemListView(TemplateView,
                        BaseLoginRequiredView,
                        ):
    """
    Renders the OrderItem management page.
    Only accessible to authenticated users.
    """
    template_name = 'orders/order_items.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Extract choices from the OrderItem model
        context['item_status_choices'] = OrderItem.STATUS_CHOICES
        context['priority_level_choices'] = OrderItem.PRIORITY_CHOICES
        context['paid_status_choices'] = Order.PAID_CHOICES

        # Serialize choices to JSON for JavaScript
        context['item_status_choices_json'] = json.dumps(
            context['item_status_choices'])
        context['priority_level_choices_json'] = json.dumps(
            context['priority_level_choices'])
        context['paid_status_choices_json'] = json.dumps(
            context['paid_status_choices'])
        return context


# define viewset that feeds the order_items API
class OrderViewSet(viewsets.ModelViewSet,
                   LoginRequiredMixin):
    """
    A ViewSet for viewing and editing Order instances.
    """
    # fetch queryset with optimised query for related objects
    queryset = Order.objects.prefetch_related('items').all().order_by('-id')
    serializer_class = OrderSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter,
                       filters.SearchFilter]
    ordering_fields = [
        'id',
        'client__client_name',
        'discount',
        'deposit',
        'order_value',
        'order_status',
        'paid'
    ]
    ordering = ['-id']  # Default ordering

    # Define fetching queryset process
    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset()

        # Check if accessing a specific object (detail view)
        if self.kwargs.get('pk') is not None:
            # Include all orders when accessing a specific object
            return queryset

        # Get query parameters if any
        order_id = self.request.query_params.get('order_id', None)
        show_archived = True if self.request.query_params.get(
            'archived', False) else False

        # If 'show_archived' is provided, return the archived queryset
        if show_archived:
            return queryset.filter(archived=True)

        # If 'order_id' is provided, return the filtered queryset
        if order_id:
            return queryset.filter(order__id=order_id)

        # Default to return the non-archived queryset
        return queryset.filter(archived=False)

    # Define deletion (destroy) process
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Store instance id before deletion
        id = instance.id
        # Delete the instance
        self.perform_destroy(instance)

        # Return response
        return response.Response(
            {'success': True,
             'message': f'Order {id} deleted.'},
            status=status.HTTP_200_OK
        )

    # Create a custom actions that responds to POST requests and
    # is performed on a single object
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        order = self.get_object()
        order.archived = True
        order.save()
        return response.Response({'success': True,
                                  'message': f'Order {order.id} archived.'},
                                 status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        order = self.get_object()
        order.archived = False
        order.save()
        return response.Response({'success': True,
                                  'message': f'Order {order.id} un-archived.'},
                                 status=status.HTTP_200_OK)


class OrderListView(TemplateView,
                    BaseLoginRequiredView,
                    ):
    """
    Renders the Order management page.
    Only accessible to authenticated users.
    """
    template_name = 'orders/orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Extract choices from the Order model
        context['order_status_choices'] = Order.STATUS_CHOICES
        context['item_status_choices'] = OrderItem.STATUS_CHOICES
        context['paid_status_choices'] = Order.PAID_CHOICES
        context['priority_level_choices'] = OrderItem.PRIORITY_CHOICES

        # Serialize choices to JSON for JavaScript
        context['order_status_choices_json'] = json.dumps(
            context['order_status_choices'])
        context['item_status_choices_json'] = json.dumps(
            context['item_status_choices'])
        context['paid_status_choices_json'] = json.dumps(
            context['paid_status_choices'])
        context['priority_level_choices_json'] = json.dumps(
            context['priority_level_choices'])

        return context


class OrderArchiveListView(TemplateView,
                           BaseLoginRequiredView,
                           ):
    template_name = 'orders/archive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Extract choices from the Order model
        context['order_status_choices'] = Order.STATUS_CHOICES
        context['item_status_choices'] = OrderItem.STATUS_CHOICES
        context['paid_status_choices'] = Order.PAID_CHOICES
        context['priority_level_choices'] = OrderItem.PRIORITY_CHOICES

        # Serialize choices to JSON for JavaScript
        context['order_status_choices_json'] = json.dumps(
            context['order_status_choices'])
        context['item_status_choices_json'] = json.dumps(
            context['item_status_choices'])
        context['paid_status_choices_json'] = json.dumps(
            context['paid_status_choices'])
        context['priority_level_choices_json'] = json.dumps(
            context['priority_level_choices'])

        return context
