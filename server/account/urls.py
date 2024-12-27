from django.urls import path

import account.views.login
import account.views.accounts
import account.views.users
import account.views.service_accounts

urlpatterns = [
    path('api/auth/login', account.views.login.LoginView.as_view(), name='login'),
    path("api/account", account.views.accounts.AccountView.as_view(), name="account"),
    path("api/users", account.views.users.UserListView.as_view(), name="user_list"),
    path("api/users/<int:id>", account.views.users.UserView.as_view(), name="user_details"),
    path("api/users/<int:id>/password", account.views.users.UserPasswordView.as_view(), name="user_password"),
    path("api/service_accounts/", account.views.service_accounts.ServiceAccountListView.as_view(),
         name="service_account_list"),
    path("api/service_accounts/<int:id>", account.views.service_accounts.ServiceAccountView.as_view()),
    path("api/service_accounts/<int:id>/reset_token", account.views.service_accounts.ResetTokenView.as_view(),
         name="reset_token"),
    path("api/service_accounts/check_name", account.views.service_accounts.CheckServiceNameView.as_view(),
         name="check_service_name"),
]
