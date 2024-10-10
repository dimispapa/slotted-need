from datetime import datetime
import json
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Client, OrderItem, Order
from .serializers import (ProdRevChartDataSerializer,
                          DebtorChartDataSerializer,
                          ItemStatusProdDataSerializer,
                          ItemStatusConfigChartDataSerializer)
from .utils import generate_unique_rgba_colors


# Template View that renders the home template
class home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

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


# The API view that provides the data for the revenue chart in JSON format
class ProductRevenueDataAPIView(APIView):
    def get(self, request, format=None):

        # Step 1: Extract Query Parameters
        revenue_min = request.query_params.get('revenue_min', None)
        revenue_max = request.query_params.get('revenue_max', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        # Step 2: Initialize Filters
        filters = Q()

        # Step 3: Apply Revenue Filters
        try:
            if revenue_min is not None:
                revenue_min = float(revenue_min)
                filters &= Q(total_revenue__gte=revenue_min)
            if revenue_max is not None:
                revenue_max = float(revenue_max)
                filters &= Q(total_revenue__lte=revenue_max)
        except ValueError:
            return Response(
                {"error":
                    "Invalid revenue_min or revenue_max. Must be numeric."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 4: Apply Date Range Filters
        try:
            if date_from:
                date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d')
                filters &= Q(
                    order_items__order__created_on__gte=date_from_parsed)
            if date_to:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d')
                filters &= Q(
                    order_items__order__created_on__lte=date_to_parsed)
        except ValueError:
            return Response(
                {"error":
                    "Invalid date_from or date_to."
                    " Expected format: YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 5: Fetch and Annotate Products to calculate revenue per product
        products = Product.objects.annotate(
            total_revenue=Coalesce(
                Sum('order_items__item_value'),
                0,
                output_field=DecimalField()
            )
        ).filter(filters).order_by('-total_revenue')

        # Step 6: Prepare data
        product_names = [product.name for product in products]
        revenue_values = [float(product.total_revenue) for product in products]

        # Step 7: Serialize data
        serializer = ProdRevChartDataSerializer(data={
            'labels': product_names,
            'values': revenue_values,
        })

        # Step 8: Validate and return data
        if serializer.is_valid():
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class DebtorBalancesAPIView(APIView):
    def get(self, request, format=None):
        # Calculate total debtor balance per client using reverse relationship
        debtors = Client.objects.filter(orders__paid=1).annotate(
            balance_owed=Coalesce(
                Sum('orders__order_value'), 0,
                output_field=DecimalField()
            )
        ).order_by('-balance_owed')

        # prepare data
        debtor_names = [debtor.client_name for debtor in debtors]
        debtor_values = [float(debtor.balance_owed) for debtor in debtors]

        # Serialize data
        serializer = DebtorChartDataSerializer(data={
            'labels': debtor_names,
            'values': debtor_values,
            'total': sum(debtor_values)
        })

        # Validate data
        if serializer.is_valid():
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ItemStatusProductAPIView(APIView):
    def get(self, request, format=None):
        # Fetch OrderItems filtering out completed orders
        order_items = OrderItem.objects.filter(completed=False)
        # Fetch products list
        products = Product.objects.all()

        # Aggregate counts by item_status
        status_counts = list(
            order_items.values(
                'item_status', 'product__name').order_by(
                    'item_status').annotate(
                        count=Count('id')))

        # Pull the mapping with status codes to human-readable labels
        status_mapping = OrderItem.STATUS_CHOICES
        # Get the item status labels
        labels = [label for label in status_mapping.values()]
        # Initialize empty datasets list
        datasets = []
        # Get unique rgba colors list using util function
        colors = generate_unique_rgba_colors(len(products), border_color=True)

        # Ensure all statuses are represented, even with zero counts
        for idx, product in enumerate(products):
            count_data = []
            # Ensure all statuses are represented, even with zero counts
            for status_code in status_mapping.keys():
                # Find if this status exists in the aggregated data
                matching = next((item for item in status_counts
                                if item['product__name'] == product.name
                                and item['item_status'] == status_code),
                                None)
                count_data.append(matching['count'] if matching else 0)

            bg_color, bd_color = colors[idx]

            dataset = {
                'label': product.name,
                'data': count_data,
                'backgroundColor': bg_color,
                'borderColor': bd_color,
                'borderWidth': 1
            }
            datasets.append(dataset)

        # Serialize the data
        serializer = ItemStatusProdDataSerializer(data={
            'labels': labels,
            'datasets': datasets,
            'total_items': int(sum(
                [sum(dataset['data'])for dataset in datasets]
            ))
        })

        # Validate and return response
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ItemStatusConfigAPIView(APIView):
    def get(self, request, format=None):
        # Fetch OrderItems filtering out made, delivered and archived orders
        order_items = OrderItem.objects.filter(
            completed=False).select_related(
            'product').prefetch_related(
            'option_values', 'item_component_finishes').order_by(
            'id')

        # Aggregate item counts by their unique configuration combo
        config_counts = {}
        for item in order_items:
            # fetch the item's configuration property
            config = item.unique_configuration
            # pass the config to the counter dict and increment by 1
            config_counts[config] = config_counts.get(config, 0) + 1

        # Sort the config_counts dict by descending on count
        sorted_config_counts = dict(sorted(config_counts.items(),
                                           key=lambda x: x[1],
                                           reverse=True))

        # Get the item status labels
        labels = [label for label in sorted_config_counts.keys()]
        # Get values of config
        values = [count for count in sorted_config_counts.values()]
        # Create list of background colors
        colors = generate_unique_rgba_colors(len(labels))

        # Serialize the data
        serializer = ItemStatusConfigChartDataSerializer(data={
            'labels': labels,
            'values': values,
            'colors': colors
        })

        # Validate and return response
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
