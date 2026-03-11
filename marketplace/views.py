from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Product, Cart, Order
from .forms import ProductForm, CheckoutForm


@login_required
def checkout_view(request):
    """View for the checkout page."""
    if request.user.user_type != 'B':
        raise PermissionDenied("Only buyers can checkout.")

    # Get all items in the user's cart
    cart_items = request.user.cart_buyer.select_related('product', 'product__store')
    if not cart_items.exists():
        return redirect('marketplace:marketplace')

    # Get unique stores from the cart items to display their QRs
    stores = set(item.product.store for item in cart_items)

    # Calculate the grand total for display
    grand_total = sum(item.subtotal for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            
            for item in cart_items:
                # Create Order instance
                Order.objects.create(
                    product=item.product,
                    buyer=request.user,
                    address=address,
                    quantity=item.quantity,
                    total_price=item.subtotal, # Based on Cart.subtotal property
                    status='P' # Set to Pending
                )
                # Update inventory stock
                item.product.stock -= item.quantity
                item.product.save()

            # Clear the cart after orders are recorded
            cart_items.delete() 
            return redirect('marketplace:order_history')
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form, 
        'cart_items': cart_items,
        'grand_total': grand_total,
        'stores': stores
    })


@login_required
def cart_view(request):
    """View for the shopping cart page."""
    # Ensure only buyers can access carts
    if request.user.user_type != 'B':
        raise PermissionDenied("Only buyers can access carts")

    if request.method == 'GET':
        cart = (request.user.cart_buyer.select_related('product', 'product__store'))
        grouped = {}
        cart_price = 0
        cart_size = 0
        for item in cart:
            store = item.product.store

            if store.id not in grouped:
                grouped[store.id] = {
                    "store": store,
                    "items": [],
                    "total_prices": {},
                }

            grouped[store.id]["items"].append(item)
            grouped[store.id]["total_prices"][item] = item.quantity * item.product.price
            cart_price += item.quantity * item.product.price
            cart_size += item.quantity
        return render(request, 'shopping_cart.html', {'cart': grouped, 'cart_price': cart_price, 'cart_size': cart_size})
    
    if request.method == 'POST':
        action = request.POST.get('action')
        product_id = int(request.POST.get('product'))
        product = Product.objects.get(pk=product_id)
        item = Cart.objects.get(product=product, buyer=request.user)
        if action == 'increase':
            if item.quantity >= item.product.stock:
                return redirect("marketplace:shopping_cart")
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity <= 0:
                return redirect("marketplace:shopping_cart")
            item.quantity += -1
            item.save()
        elif action == 'remove':
            item.delete()

    return redirect("marketplace:shopping_cart")


@login_required
def marketplace_view(request):
    """View for the marketplace page."""
    products = Product.objects.all()
    return render(request, 'marketplace.html',
                  {'products': products})


@login_required
def product_view(request, pk):
    """View for the product page."""
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'product_view.html', {'product': product})

    # add product to cart, if its not there yet
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "add-to-cart":
            if request.user.user_type != "B":
                raise PermissionDenied("Only buyers can add products to shopping cart")

            product = get_object_or_404(Product, pk=pk)
            qty = int(request.POST.get('quantity'))

            # check if already in cart
            item, created = Cart.objects.get_or_create(
                buyer = request.user,
                product = product,
                defaults={'quantity': qty}
            )

            if not created:
                if item.quantity + qty > product.stock:
                    # insert flash or warning that stock is not enough
                    return redirect("marketplace:product_view", pk=pk)
                item.quantity += qty
                item.save()
            
            # notify user thru message or flash that success!
            return redirect("marketplace:product_view", pk=pk)


@login_required
def add_product(request):
    """View for a seller to add a new product."""
    if request.user.user_type != 'S':
        raise PermissionDenied("Only sellers can add products.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = request.user.store
            product.rating = 0  
            product.save()
            return redirect('marketplace:product_view', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'product_form.html',
                  {'form': form,
                   'action': 'Add'})


@login_required
def edit_product(request, pk):
    """View for a seller to edit their existing product."""
    product = get_object_or_404(Product, pk=pk, store__seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('marketplace:product_view', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_form.html', {
        'form': form,
        'product': product,
        'action': 'Edit'
    })


@login_required
def seller_view_order_history(request):
    """View for sellers to see their transaction history."""
    if request.user.user_type != "S":
        raise PermissionDenied("Only Sellers can see their transaction history")

    store = request.user.store

    # Get only orders belonging to this seller's store
    orders = Order.objects.filter(
        product__store=store
    ).select_related('product', 'product__store', 'buyer')

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")

        order = get_object_or_404(Order, id=order_id, product__store=store)

        order.status = new_status
        order.save()

        return redirect('marketplace:transaction-history')

    return render(request, 'transaction_history.html', {
        'orders': orders
    })

@login_required
def transaction_detail(request, pk):
    """View for the transaction detail page."""
    order = get_object_or_404(Order, pk=pk)
    
    # Check if user is authorized to view this order
    is_buyer = order.buyer == request.user
    is_seller = (request.user.user_type == 'S' and 
                 order.product.store == request.user.store)
    
    if not (is_buyer or is_seller):
        raise PermissionDenied("You don't have permission to view this order")
    
    if request.method == 'POST':
        # Only sellers can update order status
        if not is_seller:
            raise PermissionDenied("Only sellers can update order status")
        
        new_status = request.POST.get("status")
        order.status = new_status
        order.save()
        return redirect('marketplace:transaction_detail', pk=pk)
    
    return render(request, 'transaction_detail.html', {'order': order})

@login_required
def order_history(request):
    """View for the buyer's order history page."""
    # This fetches orders that the logged-in user has made
    buyer_orders = Order.objects.filter(buyer=request.user).order_by('-date')
    return render(request, 'order_history.html', {'orders': buyer_orders})

def track_list(request):
    """View for the seller's product tracking list"""
    return render(request, 'seller_products.html')
