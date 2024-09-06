from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from .models import Client, Order, OrderItem
from products.models import (Option, OptionValue, Finish,
                             FinishOption)
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
            client = form.cleaned_data['client']
            # check if user selected a client
            if not client:
                # if not then create a new client object
                client = Client.objects.create(
                    client_name=form.cleaned_data['new_client_name'],
                    client_phone=form.cleaned_data['new_client_phone'],
                    client_email=form.cleaned_data['new_client_email']
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


def get_options_data(request):
    # Serialize data into JSON-serializable format
    options = list(Option.objects.values())
    option_values = list(OptionValue.objects.values())
    finishes = list(Finish.objects.values())
    finish_options = list(FinishOption.objects.values())

    return JsonResponse({
        'options': options,
        'option_values': option_values,
        'finishes': finishes,
        'finish_options': finish_options
    })
