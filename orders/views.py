from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Client, Order, OrderItem
from products.models import Product, Option, OptionValue, FinishOption
from .forms import OrderForm, OrderItemFormSet


def home(request):
    return render(request, 'orders/index.html')


def create_order(request):
    if request.method == 'POST':
        # pass the post request to the form and formset objects
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        # validation of forms and formset fields ensuring no errors
        if form.is_valid() and formset.is_valid():
            # handle client creation or selection
            client_name = form.cleaned_data['client_name']
            client_phone = form.cleaned_data['client_phone']
            client_email = form.cleaned_data['client_email']

            # try to find client by name, phone or email
            client = Client.objects.filter(
                client_name=client_name,
                client_phone=client_phone,
                client_email=client_email).first()

            if not client:
                # if a client is not found then create a new client object
                client = Client.objects.create(
                    client_name=form.cleaned_data['client_name'],
                    client_phone=form.cleaned_data['client_phone'],
                    client_email=form.cleaned_data['client_email']
                )

            # create order object
            order = Order.objects.create(client=client)

            # process each form in the formset to save the order items
            for form_item in formset:
                # create associated OrderItem instance without commiting to db
                order_item = form_item.save(commit=False)
                # pass the Order instance created above to link it with
                order_item.order = order
                # save and commit OrderItem to db
                order_item.save()
                # save the many-to-many data for option_values and finishes
                form.save_m2m()

            # notify user with success message
            messages.success(
                'Order created successfully!'
            )

            # Reset the form and formset by creating new instances
            form = OrderForm()
            formset = OrderItemFormSet(queryset=OrderItem.objects.none())

        else:
            # If the forms are not valid, display an error message
            messages.error(
                'There was an error with your submission. Please try again.'
            )

    # if a GET request simply starting a new form
    else:
        form = OrderForm()
        formset = OrderItemFormSet(queryset=OrderItem.objects.none())

    # render the template with form and formset context passed
    return render(request, 'orders/create_order.html',
                  {'form': form,
                   'formset': formset, })


def get_product_options(request, product_id):
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

    # Return the data as JSON
    return JsonResponse({
        'options': options_data,
        'finishes': finishes_data
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
