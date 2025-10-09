from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CreateOrderSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Créer une commande à partir du panier
    POST /api/orders/create/
    Body: {
        "shipping_address": "123 rue...",
        "shipping_city": "Paris",
        "shipping_postal_code": "75001",
        "shipping_phone": "+33612345678"
    }
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier que l'utilisateur a un panier
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Panier vide'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier que le panier n'est pas vide
    if cart.items.count() == 0:
        return Response({
            'status': 'error',
            'message': 'Panier vide'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Utiliser une transaction pour assurer la cohérence
    try:
        with transaction.atomic():
            # Vérifier le stock pour tous les produits
            for cart_item in cart.items.all():
                if cart_item.product.stock < cart_item.quantity:
                    return Response({
                        'status': 'error',
                        'message': f'Stock insuffisant pour {cart_item.product.name}. Stock disponible: {cart_item.product.stock}'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Créer la commande
            order = Order.objects.create(
                user=request.user,
                total=cart.total,
                shipping_address=serializer.validated_data['shipping_address'],
                shipping_city=serializer.validated_data['shipping_city'],
                shipping_postal_code=serializer.validated_data['shipping_postal_code'],
                shipping_phone=serializer.validated_data['shipping_phone']
            )

            # Créer les items de commande et décrémenter le stock
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_unit=cart_item.price_unit
                )
                # Décrémenter le stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()

            # Vider le panier
            cart.items.all().delete()

            # Retourner la commande créée
            order_serializer = OrderDetailSerializer(order)
            return Response({
                'status': 'success',
                'message': 'Commande créée avec succès',
                'data': order_serializer.data
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Erreur lors de la création de la commande'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """
    Liste des commandes de l'utilisateur
    GET /api/orders/
    """
    orders = Order.objects.filter(user=request.user)
    serializer = OrderListSerializer(orders, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Détail d'une commande
    GET /api/orders/{order_id}/
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderDetailSerializer(order)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)
