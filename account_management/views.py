from .forms import UserProfileForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

# Create your views here.


class RegisterView(FormView):
    form_class = UserProfileForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
