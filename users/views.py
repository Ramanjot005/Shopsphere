from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
class MyPasswordChangeView(PasswordChangeView):
    template_name = 'users/password-change.html'
    success_url = reverse_lazy('users:password-change-done')


class MyPasswordResetDoneView(PasswordChangeDoneView):
    template_name='users/password-reset-done.html'
# Create your views here.

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'users/update-profile.html'
    success_url = reverse_lazy('profile')