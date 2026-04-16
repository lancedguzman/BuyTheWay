from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Order, Product
from .models import Group, GroupMember


def _require_buyer(user):
    if user.user_type != 'B':
        raise PermissionDenied("Only buyers can use group features.")
    

@login_required
def create_group(request, product_pk):
    """
    POST only – called from the product page when a buyer chooses
    'Group Discount' from the Pasabuy Now dropdown.
    """
    _require_buyer(request.user)

    product = get_object_or_404(Product, pk=product_pk, group_payment=True)

    if request.method != 'POST':
        return redirect('marketplace:product_view', pk=product_pk)

    try:
        target_size = int(request.POST.get('target_size', 0))
        quantity = int(request.POST.get('quantity', 1))
        address = request.POST.get('address', '').strip()
    except (TypeError, ValueError):
        return redirect('marketplace:product_view', pk=product_pk)

    if target_size < 2 or quantity < target_size or not address:
        return redirect('marketplace:product_view', pk=product_pk)

    with transaction.atomic():
        group = Group.objects.create(
            product=product,
            creator=request.user,
            target_size=target_size,
        )
        GroupMember.objects.create(
            group=group,
            buyer=request.user,
            quantity=quantity,
            address=address,
        )

    return redirect('groupings:group_detail', pk=group.pk)


@login_required
def group_detail(request, pk):
    """
    Shows group status, member list, 
    invite link, and lock button (creator only).
    """
    _require_buyer(request.user)

    group = get_object_or_404(Group, pk=pk)

    # Only members and the creator may view this page
    is_member = group.members.filter(buyer=request.user).exists()
    if not is_member:
        raise PermissionDenied("You are not a member of this group.")

    members = group.members.select_related('buyer', 'order')

    return render(request, 'groupings/group_detail.html', {
        'group': group,
        'members': members,
        'is_creator': group.creator == request.user,
    })


@login_required
def join_group(request, token):
    """
    GET  – shows a join-confirmation page.
    POST – adds the buyer to the group.
    """
    _require_buyer(request.user)

    group = get_object_or_404(Group, invite_token=token)

    if group.status != Group.STATUS_OPEN:
        return render(request, 'groupings/group_closed.html', {'group': group})

    # Already a member – go straight to detail
    if group.members.filter(buyer=request.user).exists():
        return redirect('groupings:group_detail', pk=group.pk)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            address = request.POST.get('address', '').strip()
        except (TypeError, ValueError):
            return redirect('groupings:join_group', token=token)

        if quantity < 1 or not address:
            return redirect('groupings:join_group', token=token)

        GroupMember.objects.create(
            group=group,
            buyer=request.user,
            quantity=quantity,
            address=address,
        )
        return redirect('groupings:group_detail', pk=group.pk)

    return render(request, 'groupings/join_group.html', {'group': group})


@login_required
def lock_group(request, pk):
    """
    POST only – creator locks the group, creating one Order per member
    at group_price. Group status becomes Locked.

    Requirements (from SDD REQ-1):
        - Must have >= 2 members before locking.
    """
    _require_buyer(request.user)

    if request.method != 'POST':
        return redirect('groupings:group_detail', pk=pk)

    group = get_object_or_404(Group, pk=pk, creator=request.user)

    if group.status != Group.STATUS_OPEN:
        return redirect('groupings:group_detail', pk=pk)

    if group.member_count < 2:
        # SDD REQ-1: group must not consist of just one buyer
        return redirect('groupings:group_detail', pk=pk)

    with transaction.atomic():
        members = group.members.select_related('buyer').all()
        product = group.product

        for member in members:
            order = Order.objects.create(
                product=product,
                buyer=member.buyer,
                address=member.address,
                quantity=member.quantity,
                total_price=product.group_price * member.quantity,
                status=Order.STATUS_CHOICES[0][0],  # 'P' – Pending
            )
            # Deduct stock
            product.stock -= member.quantity
            product.save()

            # Link back so detail page can show the order
            member.order = order
            member.save(update_fields=['order'])

        group.status = Group.STATUS_LOCKED
        group.save(update_fields=['status'])

    return redirect('groupings:group_detail', pk=pk)


@login_required
def cancel_group(request, pk):
    """
    POST only – creator cancels an open group before it is locked.
    No orders are created; members are simply notified via the status change.
    """
    _require_buyer(request.user)

    if request.method != 'POST':
        return redirect('groupings:group_detail', pk=pk)

    group = get_object_or_404(Group, pk=pk, creator=request.user)

    if group.status == Group.STATUS_OPEN:
        group.status = Group.STATUS_CANCELLED
        group.save(update_fields=['status'])

    return redirect('groupings:group_detail', pk=pk)
