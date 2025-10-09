from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_unit', 'subtotal']
        read_only_fields = ['price_unit', 'subtotal']


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total', 'items_count', 'created_at']
        read_only_fields = ['total', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'total', 'items', 'items_count',
            'shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=255, required=True)
    shipping_city = serializers.CharField(max_length=100, required=True)
    shipping_postal_code = serializers.CharField(max_length=20, required=True)
    shipping_phone = serializers.CharField(max_length=20, required=True)
