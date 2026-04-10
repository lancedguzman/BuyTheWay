from .forms import UserProfileForm, BuyerProfileForm, SellerUserForm, SellerStoreForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile

# Create your views here.


class RegisterView(FormView):
    form_class = UserProfileForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('account_management:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


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
