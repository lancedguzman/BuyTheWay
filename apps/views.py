from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from marketplace.models import Product, Order, Store

# Create your views here.


def home(request):
    """View for the home page."""
    return render(request, 'base.html') #just for testing


def cart_view(request):
    """View for the shopping cart page."""
    return render(request, 'shopping_cart.html') #just for testing 2


@login_required
def marketplace_view(request):
    """View for the marketplace page."""
    products = Product.objects.all()
    return render(request, 'marketplace.html',
                  {'products': products})


def product_detail(request, pk):
    """View for the product page."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product.html', {'product': product})
