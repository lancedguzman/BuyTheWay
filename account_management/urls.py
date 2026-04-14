from django.urls import path
from .views import RegisterView, CustomLoginView, VerifyEmailView, buyer_profile, seller_profile, seller_id_verification, public_buyer_profile, public_seller_profile
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'account_management'

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', buyer_profile, name='buyer_profile'),
    path('seller-profile/', seller_profile, name='seller_profile'),
    path('id-verification/', seller_id_verification, name='id_verification'),
    path('buyer/<int:pk>/', public_buyer_profile, name='public_buyer_profile'),
    path('seller/<int:pk>/', public_seller_profile, name='public_seller_profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
     'password-reset/',
     auth_views.PasswordResetView.as_view(
          template_name='registration/password_reset_form.html',
          email_template_name='registration/password_reset_email.html',
          success_url=reverse_lazy('account_management:password_reset_done'),
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
            success_url=reverse_lazy(
                'account_management:password_reset_complete'),
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
