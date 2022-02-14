"""WordPuzzles URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from puzzles.views import HomeView, EditPuzzleView
from user_auth.views import SignUpView, UserAccountView

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', HomeView.as_view(), name="home"),
    path('signup', SignUpView.as_view(), name="signup"),
    path('login', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('password_reset', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done', auth_views.PasswordResetDoneView.as_view(template_name='password_reset.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_complete'),
    path('account', UserAccountView.as_view(), name="account"),
    path('account/edit/', UserAccountView.as_view(), name="account_edit"),

    path('new_xword_puzzle', EditPuzzleView.as_view(), name="new_xword_puzzle"),
    path('new_word_puzzle', EditPuzzleView.as_view(), name="new_word_puzzle"),
    path('edit_puzzle/<int:id>/', EditPuzzleView.as_view(), name="edit_puzzle")
]
