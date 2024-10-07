from rest_framework import serializers


class RevenueDataSerializer(serializers.Serializer):
    product_names = serializers.ListField(child=serializers.CharField())
    revenue_values = serializers.ListField(child=serializers.FloatField())
