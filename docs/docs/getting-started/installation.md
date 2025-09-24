---
sidebar_position: 1
---

# Installation

The quickest way to start using Enthusiast is with the provided Docker Compose setup. This will get you a working instance in just a few minutes.

## Prerequisites

- Docker and Docker Compose or Docker Enginer(Light weight) installed on your system
- OpenAI API key (required for AI functionality)

## Setting up using Docker Compose

### For Contributors (Main Repository)

If you're contributing to Enthusiast development, clone the main repository:

```shell
$ git clone https://github.com/upsidelab/enthusiast
$ cd enthusiast
$ cp server/sample.env server/.env
```

### For End Users (Starter Repository)

If you want to use Enthusiast for your project, use the starter repository:

```shell
$ git clone https://github.com/upsidelab/enthusiast-starter
$ cd enthusiast-starter
$ cp config/env.sample config/env
```

## Configure OpenAI API Key

:::warning Required Configuration
The application requires an OpenAI API key to function properly. Without it, you'll encounter authentication errors and the frontend won't load properly.
:::

1. **Get your OpenAI API key:**
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create a new API key

2. **Add the key to your environment file:**

   For contributors (main repo), edit `server/.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

   For end users (starter repo), edit `config/env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here


## Required Environment Variables
- `OPENAI_API_KEY`: Get from OpenAI Platform (required)
- `ECL_DJANGO_SECRET_KEY`: Generate a secure random string

## Optional Environment Variables  
- `GOOGLE_API_KEY`: For Google services integration (optional)
   ```

:::info Model Requirements
The default configuration uses the OpenAI API for generating document embeddings and for the large language model. Make sure that your OpenAI account has access to gpt-4o (recommended) or at least gpt-4o-mini to ensure proper functionality.
:::

## Start the Application

Run Docker Compose to start the environment:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="contributors" label="Contributors (Main Repo)" default>
    ```bash
    # Development environment with hot reloading
    $ docker compose -f docker-compose.development.yml up --build
    ```
  </TabItem>
  <TabItem value="users-macos-linux" label="End Users (macOS/Linux)">
    ```bash
    $ docker compose build && docker compose up
    ```
  </TabItem>
  <TabItem value="users-windows" label="End Users (Windows)">
    ```powershell
    $ docker-compose build
    $ docker-compose up
    ```
  </TabItem>
</Tabs>

:::tip Development Setup
Contributors should use the development compose file (`docker-compose.development.yml`) which includes hot reloading and development-specific configurations.
:::

## Access the Application

Once the setup is complete, you can access the application UI at [http://localhost:10001](http://localhost:10001).

![Login using the default credentials](./img/installation-login.png)

Sign in using the default admin account:

**Email**: admin@example.com

**Password**: changeme

:::note Custom Credentials
To customize the default email and password, set the ECL_ADMIN_EMAIL and ECL_ADMIN_PASSWORD environment variables when running Docker Compose for the first time.
:::

## Troubleshooting

### OpenAI Authentication Errors

If you see errors like `openai.AuthenticationError: Error code: 401` in the logs:

1. Verify your OpenAI API key is correctly set in the environment file
2. Ensure your OpenAI account has sufficient credits
3. Check that your API key has the necessary permissions

### Container Startup Issues

If containers fail to start:

```bash
# Stop all containers
$ docker compose -f docker-compose.development.yml down

# Remove volumes and rebuild
$ docker compose -f docker-compose.development.yml down -v
$ docker compose -f docker-compose.development.yml up --build --force-recreate
```

### Port Conflicts

If ports 10000 or 10001 are already in use:

1. Stop services using those ports
2. Or modify the port mappings in the docker-compose file

## Next Steps

You can now [import test data](/tools/enthusiast/docs/getting-started/import-test-data) to start exploring Enthusiast's features.