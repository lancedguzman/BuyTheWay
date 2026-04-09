import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from marketplace.models import Product
from .models import Conversation, Message


@login_required
def inbox(request):
    """List all conversations for the current user with unread counts."""
    user = request.user
    if user.user_type == 'B':
        conversations = Conversation.objects.filter(buyer=user).select_related(
            'seller', 'product'
        )
    else:
        conversations = Conversation.objects.filter(seller=user).select_related(
            'buyer', 'product'
        )

    # Annotate unread counts for the current user
    conversation_data = []
    for conv in conversations:
        unread = conv.messages.exclude(sender=user).filter(is_read=False).count()
        conversation_data.append({'conversation': conv, 'unread': unread})

    return render(request, 'chat/inbox.html', {'conversation_data': conversation_data})


@login_required
def conversation_view(request, pk):
    """View a specific conversation."""
    user = request.user
    conversation = get_object_or_404(Conversation, pk=pk)

    # Only participants can view
    if user != conversation.buyer and user != conversation.seller:
        return redirect('chat:inbox')

    # Mark messages from the other party as read
    conversation.messages.exclude(sender=user).filter(is_read=False).update(is_read=True)

    messages_qs = conversation.messages.select_related('sender').all()
    other_user = conversation.seller if user == conversation.buyer else conversation.buyer

    return render(request, 'chat/conversation.html', {
        'conversation': conversation,
        'messages': messages_qs,
        'other_user': other_user,
    })


@login_required
def start_conversation(request, product_id):
    """Start a conversation about a product."""
    product = get_object_or_404(Product, pk=product_id)
    buyer = request.user

    if buyer.user_type != 'B':
        return redirect('marketplace:product_view', pk=product_id)

    seller = product.store.seller
    conversation, _ = Conversation.objects.get_or_create(
        buyer=buyer,
        seller=seller,
        product=product,
    )
    return redirect('chat:conversation', pk=conversation.pk)


@login_required
@require_POST
def send_message(request, pk):
    """Send a message in a conversation."""
    conversation = get_object_or_404(Conversation, pk=pk)
    user = request.user

    if user != conversation.buyer and user != conversation.seller:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    attachment = None
    if request.content_type and 'multipart' in request.content_type:
        content = request.POST.get('content', '').strip()
        attachment = request.FILES.get('attachment')
    else:
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except (json.JSONDecodeError, AttributeError):
            content = request.POST.get('content', '').strip()

    if not content and not attachment:
        return JsonResponse({'error': 'Empty message'}, status=400)

    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        content=content,
        attachment=attachment,
    )

    return JsonResponse({
        'id': message.pk,
        'sender_id': user.pk,
        'sender_name': user.first_name or user.email,
        'sender_profile_picture': (
            user.profile_picture.url if user.profile_picture else None
        ),
        'content': message.content,
        'attachment_url': message.attachment.url if message.attachment else None,
        'attachment_name': message.attachment.name.split('/')[-1] if message.attachment else None,
        'timestamp': message.timestamp.strftime('%b %d, %Y %H:%M'),
    })


@login_required
def poll_messages(request, pk):
    """Poll for new messages in a conversation."""
    conversation = get_object_or_404(Conversation, pk=pk)
    user = request.user

    if user != conversation.buyer and user != conversation.seller:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    after_id = request.GET.get('after', 0)
    new_messages = conversation.messages.filter(pk__gt=after_id).select_related('sender')

    # Mark incoming messages as read
    new_messages.exclude(sender=user).filter(is_read=False).update(is_read=True)

    data = [
        {
            'id': m.pk,
            'sender_id': m.sender.pk,
            'sender_name': m.sender.first_name or m.sender.email,
            'sender_profile_picture': (
                m.sender.profile_picture.url
                if m.sender.profile_picture
                else None
            ),
            'content': m.content,
            'attachment_url': m.attachment.url if m.attachment else None,
            'attachment_name': m.attachment.name.split('/')[-1] if m.attachment else None,
            'timestamp': m.timestamp.strftime('%b %d, %Y %H:%M'),
        }
        for m in new_messages
    ]
    return JsonResponse({'messages': data})
