from django.contrib import admin
from .models import Product, Order, Store, Payment, Cart, Rating


class ProductAdmin(admin.ModelAdmin):
    """Admin interface for the Product model."""
    model = Product

    list_display = ('name', 'category',
                    'price', 'stock', 
                    'rating')
    search_fields = ('name', 'category')
    list_filter = ('category',)


class OrderAdmin(admin.ModelAdmin):
    """Admin interface for the Order model."""
    model = Order

    list_display = ('product', 'date',
                    'address', 'status')
    search_fields = ('product__name',
                     'address')
    list_filter = ('date', 'status')


class StoreAdmin(admin.ModelAdmin):
    """Admin interface for the Store model."""
    list_display = ('name', 'seller',
                    'rating', 'has_gcash',
                    'has_maya', 'has_bank')
    search_fields = ('name', 'seller__username')
    list_filter = ('seller',)

    # Custom methods to quickly see if a store has uploaded their QRs
    def has_gcash(self, obj):
        return bool(obj.gcash_qr)
    has_gcash.boolean = True
    has_gcash.short_description = 'GCash QR'

    def has_maya(self, obj):
        return bool(obj.maya_qr)
    has_maya.boolean = True
    has_maya.short_description = 'Maya QR'

    def has_bank(self, obj):
        return bool(obj.bank_qr)
    has_bank.boolean = True
    has_bank.short_description = 'Bank QR'


class CartAdmin(admin.ModelAdmin):
    """Admin interface for the Cart model."""
    model = Cart
    search_fields = ('buyer__name',)


class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for the Payment model."""
    list_display = ('order', 'payment_method',
                    'amount', 'timestamp')
    search_fields = ('order__id',)
    list_filter = ('payment_method', 'timestamp')

class RatingAdmin(admin.ModelAdmin):
    """Admin interface for the Rating (Review) model."""
    list_display = ('product', 'buyer', 'rating', 'order', 'created_at')
    search_fields = ('product__name', 'buyer__username', 'comment')
    list_filter = ('rating', 'created_at')

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Rating, RatingAdmin)