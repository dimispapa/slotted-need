from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, DecimalField
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
        # Calculate total revenue per product using reverse relationship
        products = Product.objects.annotate(
            total_revenue=Coalesce(
                Sum('order_items__item_value'), 0,
                output_field=DecimalField()
            )
        ).order_by('-total_revenue')

        # Prepare data
        product_names = [product.name for product in products]
        revenue_values = [float(product.total_revenue) for product in products]

        # Serialize data
        serializer = ProdRevChartDataSerializer(data={
            'labels': product_names,
            'values': revenue_values,
        })

        # Validate data
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
