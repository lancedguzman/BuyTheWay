from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import Product, Order, Store, Payment


User = get_user_model()


class MarketplaceModelsTest(TestCase):

    def setUp(self):
        """Set up standard data for the test cases."""
        # Create a Seller UserProfile using your custom manager
        self.seller_profile = User.objects.create_user(
            email='seller@buytheway.com',
            password='SecurePassword123!',
            user_type='S',
            phone_number='09123456789'
        )

        # Create a Buyer UserProfile using your custom manager
        self.buyer_profile = User.objects.create_user(
            email='buyer@buytheway.com',
            password='SecurePassword123!',
            user_type='B',
            phone_number='09987654321'
        )

        self.gcash_qr =  SimpleUploadedFile(name='gcash.jpg', content=b'test', content_type='image/jpeg')
        self.maya_qr = SimpleUploadedFile(name='maya.jpg', content=b'test', content_type='image/jpeg')
        self.bank_qr = SimpleUploadedFile(name='bank.jpg', content=b'test', content_type='image/jpeg')

        # Create a Store
        self.store = Store.objects.create(
            name='Tech Haven',
            description='The best tech store.',
            rating=5,
            seller=self.seller_profile,
            gcash_qr = self.gcash_qr,
            maya_qr = self.maya_qr,
            bank_qr = self.bank_qr
        )

        # Create a Base Product
        self.product = Product.objects.create(
            name='Wireless Mouse',
            store=self.store,
            location='Warehouse A',
            expected_delivery=timezone.now().date() + timedelta(days=5),
            category='T',
            price=25.00,
            stock=100,
            group_payment=False,
            description='A great wireless mouse.',
            rating=4
        )

    # --- Store Tests ---

    def test_store_fields(self):
        """Test that the Store fields are correctly set."""
        self.assertEqual(self.store.name, 'Tech Haven')
        self.assertEqual(self.store.description, 'The best tech store.')
        self.assertEqual(self.store.rating, 5)
        self.assertEqual(self.store.seller, self.seller_profile)
        self.assertIn("gcash",  self.store.gcash_qr.name)
        self.assertIn("maya",  self.store.maya_qr.name)
        self.assertIn("bank", self.store.bank_qr.name)

    def test_store_str_representation(self):
        """Test the __str__ method of the Store model."""
        self.assertEqual(str(self.store), 'Tech Haven')

    # --- Product Tests ---

    def test_product_fields(self):
        """Test that the Product fields are correctly set."""
        self.assertEqual(self.product.name, 'Wireless Mouse')
        self.assertEqual(self.product.store, self.store)
        self.assertEqual(self.product.location, 'Warehouse A')
        self.assertEqual(self.product.category, 'T')
        self.assertEqual(self.product.price, 25.00)
        self.assertEqual(self.product.stock, 100)
        self.assertFalse(self.product.group_payment)
        self.assertEqual(self.product.description, 'A great wireless mouse.')
        self.assertEqual(self.product.rating, 4)

    def test_product_str_representation(self):
        """Test the __str__ method of the Product model."""
        self.assertEqual(str(self.product), 'Wireless Mouse')

    def test_group_price_valid(self):
        """Test clean() passes when group_payment is True and group_price is set."""
        self.product.group_payment = True
        self.product.group_price = 20.00
        
        # Should not raise an exception
        try:
            self.product.clean()
        except ValidationError:
            self.fail("product.clean() raised ValidationError unexpectedly!")

    def test_group_price_invalid(self):
        """Test clean() raises ValidationError when group_payment is False but group_price is set."""
        self.product.group_payment = False
        self.product.group_price = 20.00
        
        with self.assertRaises(ValidationError) as context:
            self.product.clean()
        
        self.assertTrue('group_price' in context.exception.message_dict)

    def test_product_sold_property_no_orders(self):
        """Test the 'sold' property when a product has no orders."""
        self.assertEqual(self.product.sold, 0)

    def test_product_sold_property_with_orders(self):
        """Test the 'sold' property calculates the correct aggregate sum of quantities."""
        # Create Order 1 (Quantity: 2)
        Order.objects.create(
            product=self.product,
            address='123 Main St',
            quantity=2,
            total_price=50.00,
            buyer=self.buyer_profile
        )
        # Create Order 2 (Quantity: 3)
        Order.objects.create(
            product=self.product,
            address='456 Elm St',
            quantity=3,
            total_price=75.00,
            buyer=self.buyer_profile
        )
        
        # Total sold should be 2 + 3 = 5
        self.assertEqual(self.product.sold, 5)

    # --- Order Tests ---

    def test_order_str_representation(self):
        """Test the __str__ method of the Order model."""
        order = Order.objects.create(
            product=self.product,
            address='123 Main St',
            quantity=4,
            total_price=100.00,
            buyer=self.buyer_profile
        )
        expected_str = 'Order for Wireless Mouse - 4 items'
        self.assertEqual(str(order), expected_str)

    def test_order_default_status(self):
        """Test that the default status of a newly created order is 'Pending' ('P')."""
        order = Order.objects.create(
            product=self.product,
            address='123 Main St',
            quantity=1,
            total_price=25.00,
            buyer=self.buyer_profile
        )
        self.assertEqual(order.status, 'P')


    # --- Payment Tests ---

    def test_payment_default_method(self):
        """Test that a Payment defaults to 'gcash' if no method is specified."""
        order = Order.objects.create(
            product=self.product,
            address='123 Main St',
            quantity=1,
            total_price=25.00,
            buyer=self.buyer_profile
        )
        payment = Payment.objects.create(
            order=order,
            amount=25.00
        )
        self.assertEqual(payment.payment_method, 'gcash')

    def test_payment_str_representation(self):
        """Test the __str__ method correctly maps the payment method display name."""
        order = Order.objects.create(
            product=self.product,
            address='123 Main St',
            quantity=1,
            total_price=25.00,
            buyer=self.buyer_profile
        )
        payment = Payment.objects.create(
            order=order,
            payment_method='bank',
            amount=Decimal('25.00')
        )
        expected_str = f'Payment for Order {order.id} - Amount: 25.00 via Bank Transfer (QRPh)'
        self.assertEqual(str(payment), expected_str)

    def test_payment_one_to_one_constraint(self):
        """Test that an Order cannot have more than one Payment associated with it."""
        order = Order.objects.create(
            product=self.product,
            address='123 Main St',
            quantity=1,
            total_price=25.00,
            buyer=self.buyer_profile
        )
        
        # Create the first payment (Should succeed)
        Payment.objects.create(
            order=order,
            payment_method='maya',
            amount=25.00
        )
        
        # Attempt to create a second payment for the exact same order
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                order=order,
                payment_method='gcash',
                amount=25.00
            )
