from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from .forms import NewUserForm, UserAccountForm


class SignUpView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "signup.html", {'form': NewUserForm()})
        else:
            return redirect("home")

    def post(self, request):
        form = NewUserForm(request.POST)
        if not form.is_valid():
            return render(request, "signup.html", {'form': form})
        else:
            user = form.save()
            login(request, user)
            return redirect("home")


class UserAccountView(LoginRequiredMixin, View):

    def get(self, request):
        form = UserAccountForm(instance=request.user)
        return render(request, "account.html", {'form': form})

    def post(self, request):
        form = UserAccountForm(request.POST, instance=request.user)
        if not form.is_valid():
            return render(request, "account.html", {'form': form})
        else:
            form.save()
            return redirect("account")

