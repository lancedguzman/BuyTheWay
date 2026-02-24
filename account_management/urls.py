from django.urls import path
from .views import RegisterView, CustomLoginView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'account_management'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
     'password-reset/',
     auth_views.PasswordResetView.as_view(
          template_name='registration/password_reset_form.html',
          success_url=reverse_lazy('accounts:password_reset_done'),
     ),
     name='password_reset',
     ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]