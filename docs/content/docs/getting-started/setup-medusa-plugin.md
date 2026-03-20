# Setting Up the Medusa Plugin

Enthusiast provides a plugin for [Medusa](https://medusajs.com/) that integrates AI agents directly into the Medusa admin panel.
This enables e-commerce backoffice users to use agents like catalog enrichment, order intake, and documentation search without leaving Medusa.

This guide walks you through setting up Enthusiast and the plugin in Medusa.

## 1. Set Up Enthusiast

The first step is to set up [Enthusiast Starter](https://github.com/upsidelab/enthusiast-starter) - a pre-configured Docker Compose setup that includes all required services and a set of ready-to-use agents.

### Clone the Repository

```bash
git clone https://github.com/upsidelab/enthusiast-starter
cp config/env.sample config/env
```

### Configure Environment Variables

Open the `config/env` file and set the following:

- **`OPENAI_API_KEY`** — your OpenAI API key, required for using the language model.
- **`ECL_DJANGO_ALLOWED_HOSTS`** — if your Medusa instance runs inside a Docker container, add `"host.docker.internal"` to this list. This is the host Medusa uses to communicate with Enthusiast.

### Start the Docker Containers

Build the images and start all services:

```bash
docker compose build && docker compose up
```

### Create an Admin Service Account

The Medusa plugin authenticates with Enthusiast using a service account API key. Create one with:

```bash
docker exec -it enthusiast-starter-api-1 ./manage.py createadminserviceaccount --name Medusa
```

> The container name `enthusiast-starter-api-1` may differ in your setup. Run `docker ps` to find the correct container name for the Enthusiast API service.

Copy the returned API key — you will need it in the next section.

## 2. Install the Enthusiast Plugin in Medusa

In your Medusa project directory, follow these steps:

### Add the Enthusiast Plugin Package

```bash
yarn add @upsidelab/medusa-plugin-enthusiast
```

### Configure Environment Variables

Add the following environment variables to your Medusa project:

| Variable | Description                                                                                                       |
|---|-------------------------------------------------------------------------------------------------------------------|
| `ENTHUSIAST_API_URL` | Enthusiast instance base API URL                                                                                  |
| `ENTHUSIAST_WS_URL` | Enthusiast instance base WebSocket URL (usually the same as the API URL, with ws:// or wss:// prefix              |
| `ENTHUSIAST_SERVICE_ACCOUNT_TOKEN` | Admin service account API key from the previous step                                                              |
| `ENTHUSIAST_INTEGRATION_NAME` | Set to "Medusa"                                                                                                   |
| `ENTHUSIAST_MEDUSA_BACKEND_URL` | *(Optional)* Medusa backend URL that Enthusiast sends requests to. Defaults to `http://host.docker.internal:9000` |
| `ENTHUSIAST_MEDUSA_ADMIN_URL` | *(Optional)* Medusa admin URL. Defaults to `http://localhost:9000`                                                |

If you're running Medusa in Docker, it will most likely look like this:

```bash
ENTHUSIAST_API_URL=http://host.docker.internal:10000
ENTHUSIAST_WS_URL=ws://host.docker.internal:10000
ENTHUSIAST_SERVICE_ACCOUNT_TOKEN=<generated-service-account-token>
ENTHUSIAST_INTEGRATION_NAME=Medusa
ENTHUSIAST_MEDUSA_BACKEND_URL=http://host.docker.internal:9000
ENTHUSIAST_MEDUSA_ADMIN_URL=http://localhost:9000
```

If you're running your Medusa instance outside of Docker, you'll have to change the following two variables:

```bash
ENTHUSIAST_API_URL=http://localhost:10000
ENTHUSIAST_WS_URL=ws://localhost:10000
```

### Register the Plugin

Now it's time to register the plugin in Medusa. Add it to your `medusa-config.ts`:

```js
// medusa-config.ts

const plugins = [{
  resolve: "@upsidelab/medusa-plugin-enthusiast",
  options: {
    enthusiastApiUrl: process.env.ENTHUSIAST_API_URL,
    enthusiastWSUrl: process.env.ENTHUSIAST_WS_URL,
    enthusiastServiceAccountToken: process.env.ENTHUSIAST_SERVICE_ACCOUNT_TOKEN,
    enthusiastMedusaIntegrationName: process.env.ENTHUSIAST_INTEGRATION_NAME,
    medusaBackendUrl: process.env.ENTHUSIAST_MEDUSA_BACKEND_URL,
    medusaAdminUrl: process.env.ENTHUSIAST_MEDUSA_ADMIN_URL,
  }
}]

module.exports = defineConfig({
  // ...
  plugins
})
```

### Run Migrations

```bash
yarn medusa db:migrate
```

### Restart Your Service

Restart your Medusa instance for the changes to take effect.

## 3. Start Using Enthusiast in Medusa

Once the plugin is installed and Medusa has been restarted, open the Medusa admin panel at `http://localhost:9000/app/`.

You should see "Enthusiast" in the sidebar. On first launch, the plugin will prompt you to configure the connection and select a language model.

Once the configuration is complete, you can start interacting with the available agents.


### Troubleshooting

**Vite cache not updating (dev setups)**

In development, Vite's cache can prevent admin panel changes from appearing after installing or updating packages. Delete the cache folder — it will rebuild on restart:

```bash
rm -rf node_modules/.vite
```

**Docker `node_modules` volume issues**

If you use a Docker volume mount like:

```yaml
volumes:
  - .:/server
  - /server/node_modules
```

The anonymous `/server/node_modules` volume can override dependencies installed during image build. If new packages don't appear, remove that specific volume:

```bash
docker volume ls
docker volume rm <node_modules_volume>
```
