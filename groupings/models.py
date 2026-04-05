import uuid
from django.db import models


class Group(models.Model):
    """
    A buyer-created group for a single product.
    The group discount (product.group_price) applies once the group
    is locked with at least 2 members.
    """

    STATUS_OPEN = 'O'
    STATUS_LOCKED = 'L'
    STATUS_CANCELLED = 'X'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_LOCKED, 'Locked'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    product = models.ForeignKey(
        'marketplace.Product',
        on_delete=models.CASCADE,
        related_name='groups',
        limit_choices_to={'group_payment': True},
    )
    creator = models.ForeignKey(
        'account_management.UserProfile',
        on_delete=models.CASCADE,
        related_name='created_groups',
        limit_choices_to={'user_type': 'B'},
    )
    target_size = models.PositiveIntegerField(
        help_text="Number of buyers needed to lock the group (minimum 2).",
    )
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Group #{self.pk} – {self.product.name} ({self.get_status_display()})"

    @property
    def member_count(self):
        return self.members.count()

    @property
    def is_full(self):
        return self.member_count >= self.target_size

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.target_size < 2:
            raise ValidationError({'target_size': 'A group must have at least 2 members.'})
        if not self.product.group_payment:
            raise ValidationError({'product': 'This product does not support group payments.'})
        if self.product.group_price is None:
            raise ValidationError({'product': 'This product has no group price set.'})


class GroupMember(models.Model):
    """
    Associative entity linking a buyer to a Group.
    Each member specifies their desired quantity.
    The order FK is populated when the group is locked and orders are created.
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    buyer = models.ForeignKey(
        'account_management.UserProfile',
        on_delete=models.CASCADE,
        related_name='group_memberships',
        limit_choices_to={'user_type': 'B'},
    )
    quantity = models.PositiveIntegerField(default=1)
    address = models.CharField(max_length=255)
    order = models.OneToOneField(
        'marketplace.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_member',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'buyer')

    def __str__(self):
        return f"{self.buyer.email} in Group #{self.group.pk}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.group.status != Group.STATUS_OPEN:
            raise ValidationError('This group is no longer open for new members.')
        if self.quantity < 1:
            raise ValidationError({'quantity': 'Quantity must be at least 1.'})
