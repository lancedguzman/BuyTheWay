from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'base.html') #just for testing

def cart_view(request):
    
    return render(request, 'shopping_cart.html') #just for testing 2