from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Product, Cart, Order
from .forms import ProductForm
from decimal import Decimal

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