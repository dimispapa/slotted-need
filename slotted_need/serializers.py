from rest_framework import serializers


class ChartDatasetSerializer(serializers.Serializer):
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.FloatField())
    backgroundColor = serializers.CharField()
    borderColor = serializers.CharField()
    borderWidth = serializers.FloatField()


class ProdRevChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.FloatField())


class DebtorChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.FloatField())
    total = serializers.FloatField()


class ItemStatusProdDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=ChartDatasetSerializer())
    total_items = serializers.IntegerField()


class ItemStatusConfigChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.IntegerField())
    colors = serializers.ListField(child=serializers.CharField())
