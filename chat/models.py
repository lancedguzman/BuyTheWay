from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    Model representing a conversation 
    between a buyer and a seller.
    """
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_buyer',
        limit_choices_to={'user_type': 'B'},
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_seller',
        limit_choices_to={'user_type': 'S'},
    )
    product = models.ForeignKey(
        'marketplace.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['buyer', 'seller', 'product'],
                name='unique_conversation_with_product'
            ),
            models.UniqueConstraint(
                fields=['buyer', 'seller'],
                condition=models.Q(product__isnull=True),
                name='unique_general_conversation_without_product'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        product_name = self.product.name if self.product else 'General'
        return f'{self.buyer} <-> {self.seller} [{product_name}]'

    @property
    def last_message(self):
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender} at {self.timestamp}: {self.content[:50]}'