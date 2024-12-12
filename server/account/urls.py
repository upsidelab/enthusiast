from django.urls import path

from account import views

urlpatterns = [
    path('api/auth/login', views.LoginView.as_view(), name='login'),
    path("api/account", views.AccountView.as_view(), name="account"),
    path("api/users", views.UserListView.as_view())
]