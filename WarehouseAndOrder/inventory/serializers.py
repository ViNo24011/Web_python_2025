from rest_framework import serializers
from .models import Category, Product, Warehouse


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = '__all__'
