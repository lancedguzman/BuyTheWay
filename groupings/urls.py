from django.urls import path

from . import views

app_name = 'groupings'

urlpatterns = [
    path('create/<int:product_pk>/', views.create_group, name='create_group'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('join/<uuid:token>/', views.join_group, name='join_group'),
    path('<int:pk>/lock/', views.lock_group, name='lock_group'),
    path('<int:pk>/cancel/', views.cancel_group, name='cancel_group'),
]
