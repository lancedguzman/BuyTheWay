from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'base.html') #just for testing

def cart_view(request):
    
    return render(request, 'shopping_cart.html') #just for testing 2

def buyer_product_view(request):
    
    return render(request, 'buyer_productview.html') #just for testing 3
