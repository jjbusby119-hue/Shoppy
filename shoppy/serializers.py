from rest_framework import serializers
from .models import Product, Review, Store

class ProductSerializer(serializers.ModelSerializer):
    # This serializer is used to serialize the Product model
    class Meta:
        model = Product
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'