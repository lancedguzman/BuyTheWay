from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_view, name='marketplace'),
    path('sh-cart/', views.cart_view, name='shopping_cart'),
    path('product/<int:pk>/', views.product_view, name='product_view'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('transaction-history', views.seller_view_order_history, name='transaction-history'),
    path('orders/', views.order_history, name='order_history'),
    path('track/', views.track_list, name='track_list')
]
