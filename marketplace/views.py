from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Product, Order, Store
from .forms import ProductForm

def home(request):
    """View for the home page."""
    return render(request, 'base.html') #just for testing


def cart_view(request):
    """View for the shopping cart page."""
    return render(request, 'shopping_cart.html') #just for testing 2


def marketplace_view(request):
    """View for the marketplace page."""
    products = Product.objects.all()
    return render(request, 'marketplace.html',
                  {'products': products})


def product_detail(request, pk):
    """View for the product page."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def add_product(request):
    """View for a seller to add a new product."""
    # Ensure only sellers can add products
    if request.user.user_type != 'S':
        raise PermissionDenied("Only sellers can add products.")

    if request.method == 'POST':
        # request.FILES is required for the image upload
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.rating = 0  # Default starting rating
            product.save()
            return redirect('marketplace:product_detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'add_product.html', 
                  {'form': form, 
                   'action': 'Add'})


@login_required
def edit_product(request, pk):
    """View for a seller to edit their existing product."""
    # Fetch the product, ensuring the logged-in 
    # user is the seller of this specific item
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('marketplace:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', 
                  {'form': form, 
                   'product': product, 
                   'action': 'Edit'})
