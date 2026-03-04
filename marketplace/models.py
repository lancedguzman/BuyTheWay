from django.db import models


class Product(models.Model):
    """Model representing a product in the marketplace."""

    CATEGORY_CHOICES = [
        ('M', 'Men\'s Clothing'),
        ('W', 'Women\'s Clothing'),
        ('B', 'Beauty'),
        ('T', 'Technology'),
        ('A', 'Accessories'),
        ('H', 'Hair & Body Care'),
        ('O', 'Other'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    store = models.ForeignKey('Store', on_delete=models.CASCADE,
                              related_name='product_set')
    location = models.CharField(max_length=255)
    expected_delivery = models.DateField(null=False, blank=False)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES,
                                blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    group_payment = models.BooleanField(default=False)
    group_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    rating = models.PositiveIntegerField()

    @property
    def sold(self):
        """Calculate total items sold from orders."""
        from django.db.models import Sum
        total = self.order_set.aggregate(Sum('quantity'))['quantity__sum']
        return total if total is not None else 0

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.group_payment and self.group_price is not None:
            raise ValidationError(
                {'group_price':
                 'Group price can only be set if group payment is enabled.'})


class Order(models.Model):
    """Model representing an order in the marketplace."""

    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('S', 'Shipping'),
        ('CP', 'Completed'),
        ('X', 'Cancelled'),
    ]

    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, null=False,
                              blank=False, default='P')
    buyer = models.ForeignKey('account_management.UserProfile',
                              on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f'Order for {self.product.name} - {self.quantity} items'


class Store(models.Model):
    """Model representing a store in the marketplace."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.PositiveIntegerField()
    picture = models.ImageField(upload_to='store_images/', blank=True,
                                null=True)
    seller = models.OneToOneField('account_management.UserProfile',
                                  on_delete=models.CASCADE,
                                  related_name='store',
                                  limit_choices_to={'user_type': 'S'})
    # products = models.ManyToManyField(Product)
    gcash_qr = models.ImageField(upload_to='store_qrs/gcash/', null=True, blank=True, 
                                 help_text="Upload Store GCash QR (.jpg or .png)")
    maya_qr = models.ImageField(upload_to='store_qrs/maya/', null=True, blank=True, 
                                help_text="Upload Store Maya QR (.jpg or .png)")
    bank_qr = models.ImageField(upload_to='store_qrs/bank/', null=True, blank=True, 
                                help_text="Upload Store Bank Transfer/QRPh QR (.jpg or .png)")

    def __str__(self):
        return self.name

class Cart(models.Model):
    """
    Model representing the associative relationship 
    between buyers and the current products in their shopping cart
    """
    buyer = models.ForeignKey('account_management.UserProfile',
                              on_delete=models.CASCADE,
                              related_name='cart_buyer')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        """Calculates subtotal for the cart"""
        return self.product.price * self.quantity


class Payment(models.Model):
    """Model representing a payment in the marketplace."""

    PAYMENT_METHOD_CHOICES = [
        ('gcash', 'GCash'),
        ('maya', 'Maya'),
        ('bank', 'Bank Transfer (QRPh)'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE,
                                 related_name='payment')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, 
                                      null=False, blank=False, default='gcash')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment for Order {self.order.id} - Amount: {self.amount} via {self.get_payment_method_display()}'
