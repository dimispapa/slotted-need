from datetime import datetime
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce
from products.models import Product
from orders.models import Client, OrderItem
from .serializers import (ProdRevChartDataSerializer,
                          DebtorChartDataSerializer,
                          ItemsStatusDataSerializer)


# Template View that renders the home template
class home(TemplateView):
    template_name = 'home.html'


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
        date_filters = Q()

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
                date_filters &= Q(
                    order_items__order__created_on__gte=date_from_parsed)
            if date_to:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d')
                date_filters &= Q(
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
                Sum('order_items__item_value',
                    filter=date_filters),
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
        })

        # Validate data
        if serializer.is_valid():
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ItemStatusAPIView(APIView):
    def get(self, request, format=None):
        # Filter out OrderItems belonging to archived Orders
        order_items = OrderItem.objects.filter(order__archived=False)

        # Aggregate counts by item_status
        status_counts = order_items.values(
            'item_status').annotate(count=Count('id'))

        # Pull the mapping with status codes to human-readable labels
        status_mapping = OrderItem.STATUS_CHOICES

        # Initialize counts with zero for all statuses
        labels = []
        values = []

        # Ensure all statuses are represented, even with zero counts
        for status_code, status_label in status_mapping.items():
            labels.append(status_label)
            # Find if this status exists in the aggregated data
            matching = next((item for item in status_counts
                             if item['item_status'] == status_code), None)
            values.append(matching['count'] if matching else 0)

        # Serialize the data
        serializer = ItemsStatusDataSerializer(data={
            'labels': labels,
            'values': values,
        })

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Log serializer errors for debugging
            print(serializer.errors)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
