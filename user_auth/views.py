from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View
from .forms import NewUserForm


class NewUserView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            form = NewUserForm()
            return render(request, "new_user.html", {'form': form})
        else:
            return redirect("home")

    def post(self, request):
        form = NewUserForm(request.POST)
        if not form.is_valid():
            return render(request, "new_user.html", {'form': form})
        else:
            user = form.save()
            login(request, user)
            return redirect("home")


class LoginView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            form = AuthenticationForm()
            return render(request, "login.html", {'form': form})
        else:
            return redirect("home")

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if not form.is_valid():
            return render(request, "login.html", {'form':form})
        else:
            user = form.get_user()
            login(request, user)
            return redirect("home")

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")
