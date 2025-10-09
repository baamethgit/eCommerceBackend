from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total', 'items_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'shipping_address', 'shipping_city']
    readonly_fields = ['total', 'items_count', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'status', 'total', 'items_count')
        }),
        ('Adresse de livraison', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_phone')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_unit', 'subtotal']
    list_filter = ['order']
    search_fields = ['product__name', 'order__user__username']
    readonly_fields = ['subtotal']
