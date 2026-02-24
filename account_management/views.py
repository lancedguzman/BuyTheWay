from .forms import UserProfileForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

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
