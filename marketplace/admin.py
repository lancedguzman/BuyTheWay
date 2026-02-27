from django.contrib import admin
from .models import Product, Order, Store, Cart


class ProductAdmin(admin.ModelAdmin):
    """Admin interface for the Product model."""
    model = Product

    list_display = ('name', 'category',
                    'price', 'stock', 
                    'rating')
    search_fields = ('name', 'category')
    list_filter = ('category', 'rating')


class OrderAdmin(admin.ModelAdmin):
    """Admin interface for the Order model."""
    model = Order

    list_display = ('product', 'date', 'address')
    search_fields = ('product__name', 'address')
    list_filter = ('date',)


class StoreAdmin(admin.ModelAdmin):
    """Admin interface for the Store model."""
    model = Store

    list_display = ('name', 'rating')
    search_fields = ('name',)
    list_filter = ('rating',)

class CartAdmin(admin.ModelAdmin):
    """Admin interface for the Cart model."""
    model = Cart
    search_fields = ('buyer__name',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Cart, CartAdmin)
