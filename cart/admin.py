from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'total', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['total', 'items_count', 'created_at', 'updated_at']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'price_unit', 'subtotal']
    list_filter = ['cart']
    search_fields = ['product__name', 'cart__user__username']
    readonly_fields = ['subtotal']
