from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from products.models import Product
from .serializers import RevenueDataSerializer


# Template View that renders the home template
class home(TemplateView):
    template_name = 'home.html'


# The API view that provides the data for the revenue chart in JSON format
class RevenueDataAPIView(APIView):
    def get(self, request, format=None):
        # Calculate total revenue per product using reverse relationship
        products = Product.objects.annotate(
            total_revenue=Coalesce(
                Sum('order_items__item_value'),
                0, output_field=DecimalField()
            )
        )

        # Prepare data
        product_names = [product.name for product in products]
        revenue_values = [float(product.total_revenue) for product in products]

        # Serialize data
        serializer = RevenueDataSerializer(data={
            'product_names': product_names,
            'revenue_values': revenue_values,
        })

        # Validate data
        if serializer.is_valid():
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
