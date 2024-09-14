from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import Client, Order, OrderItem
from products.models import (Product, Option, OptionValue, FinishOption,
                             ProductComponent, Component)
from .forms import OrderForm, OrderItemFormSet


def home(request):
    return render(request, 'orders/index.html')


def create_order(request):
    if request.method == 'POST':
        # pass the post request to the form and formset objects
        order_form = OrderForm(data=request.POST)
        order_item_formset = OrderItemFormSet(data=request.POST)

        # Check if the user has confirmed using the existing client
        use_existing_client = request.POST.get('use_existing_client') == 'true'

        # validation of forms and formset fields ensuring no errors
        if order_form.is_valid() and order_item_formset.is_valid():
            # Capture calculated totals from the form
            order_value = order_form.cleaned_data['order_value']
            deposit = order_form.cleaned_data['deposit']

            # handle client creation or selection
            client_name = order_form.cleaned_data['client_name']
            client_phone = order_form.cleaned_data['client_phone']
            client_email = order_form.cleaned_data['client_email']

            # Initialize the variable to avoid UnboundLocalError
            existing_client = None

            if not use_existing_client:
                # Attempt to find an existing client with a case-insensitive
                # partial match (match name and phone or email to avoid
                # duplicates)
                # Check for an exact case-insensitive match across all fields
                exact_match_client = Client.objects.filter(
                    client_name__iexact=client_name,
                    client_phone__iexact=client_phone,
                    client_email__iexact=client_email
                ).first()

                # If an exact match is found, skip the modal
                if exact_match_client:
                    client = exact_match_client

                else:
                    # If no exact match, attempt partial match
                    # (name and one of phone or email matches)
                    existing_client = Client.objects.filter(
                        Q(client_name__iexact=client_name) &
                        (Q(client_phone__iexact=client_phone) |
                         Q(client_email__iexact=client_email))
                    ).first()

                    if existing_client:
                        # Trigger modal asking user to confirm their choice and
                        # Pass the existing client data to the template
                        return render(request, 'orders/create_order.html', {
                            'order_form': order_form,
                            'order_item_formset': order_item_formset,
                            'existing_client': existing_client,
                            'show_client_modal': True  # Flag to show modal
                        })

            # If no modal is needed, proceed with saving the client and order
            client = (existing_client
                      if existing_client
                      else Client.objects.create(
                          client_name=client_name,
                          client_phone=client_phone,
                          client_email=client_email
                      ))

            # create order object
            order = Order.objects.create(
                client=client,
                order_value=order_value,
                deposit=deposit
                )

            # process each form in the formset to save the order items
            for form_item in order_item_formset:
                # create associated OrderItem instance without commiting to db
                order_item = form_item.save(commit=False)
                # pass the Order instance created above to link it with
                order_item.order = order
                # save and commit OrderItem to db
                order_item.save()
                # save the many-to-many data for option_values and finishes
                form_item.save_m2m()

            # notify user with success message
            messages.add_message(request, messages.SUCCESS,
                                 'Order created successfully!'
                                 )

            # Redirect to the same page to avoid form resubmission
            return redirect(reverse('create_order'))

        else:
            # If the forms are not valid, log errors for debugging
            print("Order form errors: ", order_form.errors)
            print("Order item formset errors: ", order_item_formset.errors)

            # If the forms are not valid, display an error message
            messages.add_message(request, messages.ERROR,
                                 'There was an error with your submission. '
                                 'Please try again.'
                                 )

            # render the page again but retaining the details
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
    return render(request, 'orders/create_order.html',
                  {'order_form': order_form,
                   'order_item_formset': order_item_formset, })


def get_products(request):
    products = Product.objects.all()
    product_data = [{'id': product.id, 'name': product.name}
                    for product in products]
    return JsonResponse({'products': product_data})


def get_product_data(request, product_id):
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


# create a get_component_finishes API function to handle the finish options
# based on the product options selected (associated with components)
def get_finishes(request, product_id, option_value_id):
    # get the option_value object and its associated product_component tables
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
                'component_name': component.name,
                'component_slug': component.slug,
                'id': finish.id,
                'name': finish.name,
                'finish_options': finish_options_data
            })

    # Return the data as JSON
    return JsonResponse({
        'component_finishes': component_finishes
    })


# create search_clients API function to deal with the query request
def search_clients(request):
    query = request.GET.get('q', '')
    if query:
        # filter the client objects based on client name, limit to 10 results
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
