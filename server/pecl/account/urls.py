from django.urls import path

from account import views

urlpatterns = [
    path('api/auth/login', views.LoginView.as_view(), name='login')
]