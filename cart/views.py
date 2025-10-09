from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from products.models import Product
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_detail(request):
    """
    Récupérer le panier de l'utilisateur connecté
    GET /api/cart/
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart, context={'request': request})
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Ajouter un produit au panier
    POST /api/cart/add/
    Body: {"product_id": 1, "quantity": 2}
    """
    serializer = AddToCartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    product_id = serializer.validated_data['product_id']
    quantity = serializer.validated_data['quantity']

    # Vérifier que le produit existe
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Vérifier le stock
    if product.stock < quantity:
        return Response({
            'status': 'error',
            'message': f'Stock insuffisant. Stock disponible: {product.stock}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Récupérer ou créer le panier
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Vérifier si le produit est déjà dans le panier
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity, 'price_unit': product.price}
    )

    if not item_created:
        # Produit déjà dans le panier, on met à jour la quantité
        new_quantity = cart_item.quantity + quantity
        if product.stock < new_quantity:
            return Response({
                'status': 'error',
                'message': f'Stock insuffisant. Stock disponible: {product.stock}'
            }, status=status.HTTP_400_BAD_REQUEST)
        cart_item.quantity = new_quantity
        cart_item.save()

    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response({
        'status': 'success',
        'message': 'Produit ajouté au panier',
        'data': cart_serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Modifier la quantité d'un item du panier
    PATCH /api/cart/update/{item_id}/
    Body: {"quantity": 3}
    """
    serializer = UpdateCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    quantity = serializer.validated_data['quantity']

    # Récupérer l'item du panier de l'utilisateur
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Vérifier le stock
    if cart_item.product.stock < quantity:
        return Response({
            'status': 'error',
            'message': f'Stock insuffisant. Stock disponible: {cart_item.product.stock}'
        }, status=status.HTTP_400_BAD_REQUEST)

    cart_item.quantity = quantity
    cart_item.save()

    cart_serializer = CartSerializer(cart_item.cart, context={'request': request})
    return Response({
        'status': 'success',
        'message': 'Quantité mise à jour',
        'data': cart_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """
    Retirer un produit du panier
    DELETE /api/cart/remove/{item_id}/
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()

    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response({
        'status': 'success',
        'message': 'Produit retiré du panier',
        'data': cart_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    Vider complètement le panier
    DELETE /api/cart/clear/
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            'status': 'success',
            'message': 'Panier vidé',
            'data': cart_serializer.data
        }, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({
            'status': 'success',
            'message': 'Panier déjà vide',
            'data': None
        }, status=status.HTTP_200_OK)
