from rest_framework import serializers

from input.models import Item
from my_app.models import BomModel


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class BomSerializer(serializers.ModelSerializer):
    class Meta:
        model = BomModel
        fields = '__all__'


class BomCalculateSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")
    qty = serializers.IntegerField(label="数量")

    class Meta:
        model = BomModel
        fields = '__all__'
