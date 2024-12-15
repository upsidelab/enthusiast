from django.urls import path

import account.views.login
import account.views.accounts
import account.views.users

urlpatterns = [
    path('api/auth/login', account.views.login.LoginView.as_view(), name='login'),
    path("api/account", account.views.accounts.AccountView.as_view(), name="account"),
    path("api/users", account.views.users.UserListView.as_view(), name="user_list"),
    path("api/users/<int:id>", account.views.users.UserView.as_view(), name="user_details"),
    path("api/users/<int:id>/password", account.views.users.UserPasswordView.as_view(), name="user_password")
]