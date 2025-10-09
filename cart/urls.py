from django.urls import path
from .views import (
    cart_detail,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart
)

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/', add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear/', clear_cart, name='clear_cart'),
]
