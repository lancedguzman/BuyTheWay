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
    seller = models.ForeignKey('account_management.UserProfile', on_delete=models.CASCADE, 
                               related_name='products', limit_choices_to={'user_type': 'S'})
    description = models.TextField()
    stock = models.PositiveIntegerField()
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    rating = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    location = models.CharField(max_length=255)

    @property
    def sold(self):
        """Calculate total items sold from orders."""
        from django.db.models import Sum
        total = self.order_set.aggregate(Sum('quantity'))['quantity__sum']
        return total if total is not None else 0

    def __str__(self):
        return self.name
    

class Order(models.Model):
    """Model representing an order in the marketplace."""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()  # Will clarify if we can add attributes not mentioned in the ERD, if not, I will remove this attribute
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order for {self.product.name} - {self.quantity} items'


class Store(models.Model):
    """Model representing a store in the marketplace."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.PositiveIntegerField()
    picture = models.ImageField(upload_to='store_images/', blank=True, null=True)
    # products = models.ManyToManyField(Product)

    def __str__(self):
        return self.name
