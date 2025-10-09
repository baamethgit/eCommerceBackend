from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all() if item.subtotal is not None)

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all() if item.quantity is not None)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_unit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart}"

    @property
    def subtotal(self):
        if self.quantity is not None and self.price_unit is not None:
            return self.quantity * self.price_unit
        return None

    def save(self, *args, **kwargs):
        # Sauvegarder le prix unitaire du produit si pas déjà défini
        if not self.price_unit:
            self.price_unit = self.product.price
        super().save(*args, **kwargs)
