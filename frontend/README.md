# E-Commerce LLM Frontend

This is a repository that contains the frontend part of the system.

## Getting started

1. Install nodejs (20+) and [pnpm](https://pnpm.io/) on your machine 
2. Run `pnpm install`
3. Set `VITE_API_BASE` env variable to point to your backend (e.g. `VITE_API_BASE=http://localhost:8000`)
4. Make sure that your backend instance has the CORS headers set correctly (i.e. set `ECL_DJANGO_CORS_ALLOWED_ORIGINS=["http://localhost:5173"]`) 
5. To develop locally run `pnpm run dev`

## Building the application
Note: you should build the application before each merge to main branch. Please do not merge, if there are any build errors.
1. Run `pnpm build`


## Known issues
### 404 on api requests
You see 404 error on api requests and address contains "undefined" in url, for example: http://localhost/undefined/api/ask.

Solution: you have to export VITE_API_BASE.

### 401 on api requests
You have to set environment variable with token of your CustomUser.

#### How to set password for CustomUser
Log into shell ```python3 manage.py shell```

Run below commands:
```
from account.models import CustomUser
# Get the user whose password you want to change
user = CustomUser.objects.get(email='dale.cooper@example.com')
# Set the new password
user.set_password('OwlsAreNotWhatTheySeem')
# Save the user to apply the changes
user.save()
```
#### How to get token and set environment variable
```
from rest_framework.authtoken.models import Token
from account.models import CustomUser

# Get the user whose password you want to change
user = CustomUser.objects.get(email='dale.cooper@example.com')

token = Token.objects.get(user=user)
print(token)
```
Move to terminal where you run your django server, run
```
export ECL_PREVIEW_API_TOKEN='your-cool-token' 
```
...and run the server
```
python3 manage.py runserver
```