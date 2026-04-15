from .forms import UserProfileForm, BuyerProfileForm, SellerUserForm, SellerStoreForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, EmailVerificationToken

# Create your views here.


class RegisterView(FormView):
    form_class = UserProfileForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('account_management:login')

    def form_valid(self, form):
        user = form.save()

        # Deactivate until email is verified
        user.is_active = False
        user.save(update_fields=['is_active'])

        # Generate and store OTP
        otp = EmailVerificationToken.generate_otp()
        EmailVerificationToken.objects.update_or_create(
            user=user,
            defaults={'otp': otp},
        )

        # Send OTP email
        send_mail(
            subject='Your BuyTheWay verification code',
            message=f'Your 6-digit verification code is: {otp}\n\nThis code expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=(
                f'<p>Your BuyTheWay verification code is:</p>'
                f'<h2 style="letter-spacing:0.3em">{otp}</h2>'
                f'<p>This code expires in <strong>10 minutes</strong>.</p>'
            ),
        )

        # Pass the user id via session so the verify view knows who to verify
        self.request.session['verify_user_id'] = user.id
        return redirect('account_management:verify_email')
    template_name = 'registration/verify_email.html'

    def _get_pending_user(self):
        user_id = self.request.session.get('verify_user_id')
        if not user_id:
            return None
        return get_object_or_404(UserProfile, pk=user_id, is_active=False)

    def get(self, request, *args, **kwargs):
        user = self._get_pending_user()
        if not user:
            return redirect('account_management:signup')

        def mask_email(email):
            local, domain = email.split('@', 1)
            masked_local = local[:2] + 'x' * (len(local) - 2)
            masked_domain = 'x' * len(domain.split('.')[0]) + '.' + '.'.join(domain.split('.')[1:])
            return f"{masked_local}@{masked_domain}"

        return render(request, self.template_name, {
            'masked_email': mask_email(user.email),
        })

    def post(self, request, *args, **kwargs):
        user = self._get_pending_user()
        if not user:
            return redirect('account_management:signup')

        # Collect OTP from six individual digit inputs
        digits = [request.POST.get(f'digit_{i}', '') for i in range(1, 7)]
        entered_otp = ''.join(digits).strip()

        try:
            token = user.email_verification
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, 'No verification token found. Please sign up again.')
            return redirect('account_management:signup')

        if token.is_expired():
            messages.error(request, 'Your code has expired. Please sign up again.')
            token.delete()
            user.delete()
            del request.session['verify_user_id']
            return redirect('account_management:signup')

        if entered_otp != token.otp:
            def mask_email(email):
                local, domain = email.split('@', 1)
                masked_local = local[:2] + 'x' * (len(local) - 2)
                masked_domain = 'x' * len(domain.split('.')[0]) + '.' + '.'.join(domain.split('.')[1:])
                return f"{masked_local}@{masked_domain}"

            messages.error(request, 'Incorrect code. Please try again.')
            return render(request, self.template_name, {
                'masked_email': mask_email(user.email),
            })

        # OTP is correct — activate the account
        user.is_active = True
        user.is_email_verified = True
        user.save(update_fields=['is_active', 'is_email_verified'])
        token.delete()
        del request.session['verify_user_id']

        messages.success(request, 'Email verified! You can now log in.')
        return redirect('account_management:login')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'


@login_required
def buyer_profile(request):
    if request.user.user_type != 'B':
        raise PermissionDenied("This page is for buyers only.")

    user = request.user

    def mask_email(email):
        local, domain = email.split('@', 1)
        return local[:2] + '*' * (len(local) - 2) + '@' + domain

    def mask_phone(phone):
        return '*' * (len(phone) - 2) + phone[-2:]

    if request.method == 'POST':
        form = BuyerProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('account_management:buyer_profile')
    else:
        form = BuyerProfileForm(instance=user)

    context = {
        'form': form,
        'masked_email': mask_email(user.email),
        'masked_phone': mask_phone(user.phone_number) if user.phone_number else '',
    }
    return render(request, 'buyer_profile.html', context)


@login_required
def seller_profile(request):
    if request.user.user_type != 'S':
        raise PermissionDenied("This page is for sellers only.")

    user = request.user
    store = user.store

    def mask_email(email):
        local, domain = email.split('@', 1)
        return local[:2] + '*' * (len(local) - 2) + '@' + domain

    def mask_phone(phone):
        return '*' * (len(phone) - 2) + phone[-2:]

    if request.method == 'POST':
        user_form = SellerUserForm(request.POST, instance=user)
        store_form = SellerStoreForm(request.POST, request.FILES, instance=store)
        if user_form.is_valid() and store_form.is_valid():
            user_form.save()
            store_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('account_management:seller_profile')
    else:
        user_form = SellerUserForm(instance=user)
        store_form = SellerStoreForm(instance=store)

    context = {
        'user_form': user_form,
        'store_form': store_form,
        'store': store,
        'masked_email': mask_email(user.email),
        'masked_phone': mask_phone(user.phone_number) if user.phone_number else '',
    }
    return render(request, 'seller_profile.html', context)


@login_required
def public_buyer_profile(request, pk):
    buyer = get_object_or_404(UserProfile, pk=pk, user_type='B')
    return render(request, 'public_buyer_profile.html', {'buyer': buyer})


@login_required
def public_seller_profile(request, pk):
    seller = get_object_or_404(UserProfile, pk=pk, user_type='S')
    store = seller.store
    products = store.product_set.all()
    return render(request, 'public_seller_profile.html', {
        'seller': seller,
        'store': store,
        'products': products,
    })
