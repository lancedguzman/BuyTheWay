from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import Conversation, Message
from marketplace.models import Product, Store


User = get_user_model()


class ChatModelsSetUpMixin:
    """Shared setUp logic for chat model tests."""

    def setUp(self):
        self.buyer = User.objects.create_user(
            email='buyer@buytheway.com',
            password='SecurePassword123!',
            user_type='B',
            phone_number='09123456789',
            first_name='Juan',
            last_name='Dela Cruz',
        )
        self.seller = User.objects.create_user(
            email='seller@buytheway.com',
            password='SecurePassword123!',
            user_type='S',
            phone_number='09987654321',
            first_name='Maria',
            last_name='Clara',
        )
        self.store = Store.objects.create(
            name='Tech Haven',
            description='The best tech store.',
            rating=5,
            seller=self.seller,
        )
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
            rating=4,
        )
        self.conversation = Conversation.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            product=self.product,
        )


class ConversationModelTest(ChatModelsSetUpMixin, TestCase):

    def test_conversation_creation(self):
        """A Conversation is saved with the correct buyer, seller, and product."""
        self.assertEqual(self.conversation.buyer, self.buyer)
        self.assertEqual(self.conversation.seller, self.seller)
        self.assertEqual(self.conversation.product, self.product)

    def test_conversation_created_at_auto_set(self):
        """created_at is set automatically on save."""
        self.assertIsNotNone(self.conversation.created_at)

    def test_str_with_product(self):
        """__str__ includes the product name when a product is linked."""
        expected = f'{self.buyer} <-> {self.seller} [Wireless Mouse]'
        self.assertEqual(str(self.conversation), expected)

    def test_str_without_product(self):
        """__str__ shows 'General' when no product is linked."""
        convo = Conversation.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            product=None,
        )
        expected = f'{self.buyer} <-> {self.seller} [General]'
        self.assertEqual(str(convo), expected)

    def test_duplicate_conversation_raises_integrity_error(self):
        """Creating a duplicate (buyer, seller, product) conversation raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Conversation.objects.create(
                buyer=self.buyer,
                seller=self.seller,
                product=self.product,
            )

    def test_same_participants_different_products_allowed(self):
        """The same buyer and seller can have separate conversations per product."""
        second_product = Product.objects.create(
            name='Mechanical Keyboard',
            store=self.store,
            location='Warehouse B',
            expected_delivery=timezone.now().date() + timedelta(days=7),
            category='T',
            price=75.00,
            stock=50,
            group_payment=False,
            description='A clicky keyboard.',
            rating=5,
        )
        second_convo = Conversation.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            product=second_product,
        )
        self.assertNotEqual(self.conversation.pk, second_convo.pk)

    def test_null_product_allows_only_one_general_conversation(self):
        """Two product-less conversations between the same pair raise IntegrityError."""
        Conversation.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            product=None,
        )
        with self.assertRaises(IntegrityError):
            Conversation.objects.create(
                buyer=self.buyer,
                seller=self.seller,
                product=None,
            )

    def test_product_deleted_sets_null(self):
        """Deleting a product sets conversation.product to NULL instead of cascading."""
        self.product.delete()
        self.conversation.refresh_from_db()
        self.assertIsNone(self.conversation.product)

    def test_buyer_related_name(self):
        """Conversations are accessible via buyer.conversations_as_buyer."""
        self.assertIn(self.conversation, self.buyer.conversations_as_buyer.all())

    def test_seller_related_name(self):
        """Conversations are accessible via seller.conversations_as_seller."""
        self.assertIn(self.conversation, self.seller.conversations_as_seller.all())

    def test_last_message_returns_none_when_no_messages(self):
        """last_message is None when the conversation has no messages."""
        self.assertIsNone(self.conversation.last_message)

    def test_last_message_returns_most_recent(self):
        """last_message returns the most recently timestamped message."""
        Message.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            content='Hello!',
        )
        msg2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            content='Hi there!',
        )
        self.assertEqual(self.conversation.last_message, msg2)

    def test_ordering_most_recent_first(self):
        """Conversations are returned newest-first by default."""
        second_buyer = User.objects.create_user(
            email='buyer2@buytheway.com',
            password='SecurePassword123!',
            user_type='B',
            phone_number='09111111111',
        )
        second_convo = Conversation.objects.create(
            buyer=second_buyer,
            seller=self.seller,
            product=self.product,
        )
        conversations = list(Conversation.objects.all())
        self.assertEqual(conversations[0], second_convo)
        self.assertEqual(conversations[1], self.conversation)


class MessageModelTest(ChatModelsSetUpMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            content='Is this still available?',
        )

    def test_message_creation(self):
        """A Message is saved with the correct conversation, sender, and content."""
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.sender, self.buyer)
        self.assertEqual(self.message.content, 'Is this still available?')

    def test_message_timestamp_auto_set(self):
        """timestamp is set automatically on save."""
        self.assertIsNotNone(self.message.timestamp)

    def test_message_is_read_default_false(self):
        """is_read defaults to False for a new message."""
        self.assertFalse(self.message.is_read)

    def test_str_short_content(self):
        """__str__ includes sender, timestamp, and the full content when ≤50 chars."""
        expected = f'{self.buyer} at {self.message.timestamp}: Is this still available?'
        self.assertEqual(str(self.message), expected)

    def test_str_long_content_truncated_to_50_chars(self):
        """__str__ truncates content to the first 50 characters."""
        long_content = 'A' * 100
        msg = Message.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            content=long_content,
        )
        expected = f'{self.seller} at {msg.timestamp}: {"A" * 50}'
        self.assertEqual(str(msg), expected)

    def test_mark_message_as_read(self):
        """is_read can be updated to True."""
        self.message.is_read = True
        self.message.save()
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_messages_deleted_when_conversation_deleted(self):
        """Deleting a conversation cascades and removes its messages."""
        msg_pk = self.message.pk
        self.conversation.delete()
        self.assertFalse(Message.objects.filter(pk=msg_pk).exists())

    def test_messages_deleted_when_sender_deleted(self):
        """Deleting the sender cascades and removes their sent messages."""
        msg_pk = self.message.pk
        self.buyer.delete()
        self.assertFalse(Message.objects.filter(pk=msg_pk).exists())

    def test_conversation_messages_related_name(self):
        """Messages are accessible via conversation.messages."""
        self.assertIn(self.message, self.conversation.messages.all())

    def test_sender_sent_messages_related_name(self):
        """Messages are accessible via sender.sent_messages."""
        self.assertIn(self.message, self.buyer.sent_messages.all())

    def test_messages_ordered_by_timestamp_ascending(self):
        """Messages within a conversation are returned oldest-first."""
        msg2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            content='Yes, still available!',
        )
        messages = list(self.conversation.messages.all())
        self.assertEqual(messages[0], self.message)
        self.assertEqual(messages[1], msg2)

    def test_multiple_messages_in_conversation(self):
        """Multiple messages can belong to the same conversation."""
        Message.objects.create(
            conversation=self.conversation,
            sender=self.seller,
            content='Yes, still available!',
        )
        Message.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            content='Great, I will buy it.',
        )
        self.assertEqual(self.conversation.messages.count(), 3)
