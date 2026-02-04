from django.urls import include, path

import account.views.accounts
import account.views.auth
import account.views.service_accounts
import account.views.users

urlpatterns = [
    path("api/auth/login", account.views.auth.LoginView.as_view(), name="login"),
    path("api/auth/logout", account.views.auth.LogoutView.as_view(), name="logout"),
    path("api/auth/csrf", account.views.auth.CSRFView.as_view(), name="csrf"),
    path("api/account", account.views.accounts.AccountView.as_view(), name="account"),
    path("api/users", account.views.users.UserListView.as_view(), name="user_list"),
    path("api/users/<int:id>", account.views.users.UserView.as_view(), name="user_details"),
    path("api/users/<int:id>/password", account.views.users.UserPasswordView.as_view(), name="user_password"),
    path(
        "api/service_accounts/",
        account.views.service_accounts.ServiceAccountListView.as_view(),
        name="service_account_list",
    ),
    path("api/service_accounts/<int:id>", account.views.service_accounts.ServiceAccountView.as_view()),
    path(
        "api/service_accounts/<int:id>/reset_token",
        account.views.service_accounts.ResetTokenView.as_view(),
        name="reset_token",
    ),
    path(
        "api/service_accounts/check_name",
        account.views.service_accounts.CheckServiceNameView.as_view(),
        name="check_service_name",
    ),
    path("login/sso/", account.views.auth.SSOProviderLoginView.as_view(), name="sso-login"),
    path("", include("social_django.urls", namespace="social")),
]
