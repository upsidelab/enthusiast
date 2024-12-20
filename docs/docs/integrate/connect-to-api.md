---
sidebar_position: 2
---

# Connect to Enthusiast's API

Once you have the API token for a service account, you can connect to Enthusiast's API.

## Trying out the API Using Swagger UI

### Authorization

1. In the main sidebar, click **API Documentation**. Swagger UI will open in a new tab.
2. In Swagger UI, click Authorize in the top-right corner.
3. Enter `Token <API_TOKEN>` in the authorization field and click **Authorize**.

:::success
You can now interact with the API. Let’s query some data.
:::

## Navigating the Endpoints

The Swagger UI lists all available endpoints organized by functionality. You can test an endpoint directly from your browser using the **Try it out** feature.

### Example: Retrieving Data Sets with GET /api/data_sets

1. Find the `GET /api/data_sets` endpoint in the list.
2. Expand the endpoint by clicking on it.
3. Click **Try it out**.
4. Click **Execute** to send the request.

## Using `curl`

To authenticate with Enthusiast's API using `curl` from the terminal, include the API token in the header of each request:

- **GET and DELETE Request**:
  ```bash
  curl -X 'GET/DELETE' \
    'http://localhost:8000/api/<PATH>' \
    -H 'accept: application/json' \
    -H 'Authorization: Token <API_TOKEN>'
    ```
  
- **POST, PUT and PATCH Request**:
    ```bash
    curl -X 'POST/PUT/PATCH' \
        'http://localhost:8000/api/<PATH>' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -H 'Authorization: Token <API_TOKEN>' \
        -d '{
        "key": "value"
        }'
    ```

:::info
Replace `<API_TOKEN>` with your actual API token and `<PATH>>` with the specific API endpoint.
:::

Example `curl` command:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/data_sets' \
  -H 'accept: application/json' \
  -H 'Authorization: Token <API_TOKEN>'
```
