---
sidebar_position: 1
---

# Manage API Keys

Service accounts enable you to integrate external systems with Enthusiast. Like user accounts, service accounts can be assigned permissions for specific datasets. 

## Creating a Service Account

1. Log in as an admin user.
2. Navigate to Manage → Service Accounts.
3. Click New Service Account.
4. Enter a name for the service account.
5. Select the data sets the account should have access to.
6. Ensure the Active checkbox is selected.
7. Click Create.
8. A pop-up will display the API token for the newly created account. Copy it and store it in a secure location.

:::success
Congratulations! You’ve successfully created a service account. Now you can [connect to Enthusiast's API](/docs/integrate/connect-to-api).
:::

## Modifying Data Set Access for a Service Account

1. Log in as an admin user.
2. Navigate to Manage → Service Accounts.
3. Click Edit next to the service account you want to update.
4. Adjust the data sets the account can access.
5. Click Update.

## Disabling a Service Account

1. Log in as an admin user.
2. Navigate to Manage → Service Accounts.
3. Click Edit next to the service account you want to disable.
4. Uncheck the Active checkbox.
5. Click Update.
6. The account is now disabled, and its API token can no longer be used.

## Resetting an API Token

1. Log in as an admin user.
2. Navigate to Manage → Service Accounts.
3. Click Reset Token next to the service account you want to update.
4. A new token will be displayed. Copy it and store it in a secure location.
5. The old token becomes invalid immediately.
