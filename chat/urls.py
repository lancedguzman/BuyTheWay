from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:pk>/', views.conversation_view, name='conversation'),
    path('start/<int:product_id>/', views.start_conversation, name='start_conversation'),
    path('<int:pk>/send/', views.send_message, name='send_message'),
    path('<int:pk>/poll/', views.poll_messages, name='poll_messages'),
]
