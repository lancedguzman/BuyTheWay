from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('sh-cart/', views.cart_view, name='shopping_cart'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
]
