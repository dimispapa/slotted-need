from django.shortcuts import render
from django.contrib import messages
from django.forms import modelformset_factory
from .models import Order, OrderItem
from .forms import OrderItemForm


def home(request):
    return render(request, 'orders/index.html')


def create_order(request):
    # create a formset object to allow multiple forms in the same view
    OrderItemFormSet = modelformset_factory(OrderItem,
                                            form=OrderItemForm,
                                            extra=1)

    if request.method == 'POST':
        # pass the post request to the formset object
        formset = OrderItemFormSet(request.POST)
        # validation of forms in formset fields ensuring no errors
        if formset.is_valid():
            # create an Order object instance with info from the post request
            order = Order.objects.create(
                customer_name=request.POST.get('customer_name'),
                customer_phone=request.POST.get('customer_phone'),
                customer_email=request.POST.get('customer_email')
            )
            # process each form in the formset
            for form in formset:
                # create associated OrderItem instance without commiting to db
                order_item = form.save(commit=False)
                # pass the Order instance crated above to link it with
                order_item.order = order
                # save and commit OrderItem to db
                order_item.save()
                # save the many-to-many data for option_values and finishes
                form.save_m2m()

            # notify user with success message
            messages.add_message(
                request, messages.SUCCESS,
                'Order submitted successfully'
            )

            # reset the form with no pre-loaded order items
            formset = OrderItemFormSet(queryset=OrderItem.objects.none())

    # if a GET request simply starting a new form
    else:
        formset = OrderItemFormSet(queryset=OrderItem.objects.none())

    # render the template with formset context passed
    return render(request, 'orders/create_order.html', {'formset': formset})
