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
from django.urls import path, include
from user_auth.views import SignOutView, SignUpView, SignInView
from puzzles.views import HomeView, EditPuzzleView

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', HomeView.as_view(), name="home"),
    path('login', SignInView.as_view(), name='login'),
    path('signup', SignUpView.as_view(), name="signup"),
    path('logout', SignOutView.as_view(), name="logout"),

    path('new_xword_puzzle', EditPuzzleView.as_view(), name="new_xword_puzzle"),
    path('new_word_puzzle', EditPuzzleView.as_view(), name="new_word_puzzle"),
    path('edit_puzzle/<int:id>/', EditPuzzleView.as_view(), name="edit_puzzle")
]
