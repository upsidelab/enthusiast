---
sidebar_position: 1
---

# Installation

The quickest way to start using Enthusiast is with the provided Docker Compose setup. This will get you a working instance in just a few minutes.

## Setting up using Docker Compose

First, clone the application repository:

```shell
$ git clone https://github.com/upsidelab/enthusiast
```

:::info
The default configuration uses the OpenAI API for generating document embeddings and for the large language model.
You need to provide your OpenAI API key via the OPENAI_API_KEY environment variable.
:::

Next, run Docker Compose to start the environment:

```shell
$ OPENAI_API_KEY=<yourkey> docker compose -f docker-compose.development.yml up -d 
```

Once the setup is complete, you can access the application UI at [http://localhost:10001](http://localhost:10001).

! TODO: SCREENSHOT HERE

Sign in using the default admin account:

**Email**: admin@example.com

**Password**: changeme

:::note
To customize the default email and password, set the ECL_ADMIN_EMAIL and ECL_ADMIN_PASSWORD environment variables when running Docker Compose for the first time.
:::
You can now [import test data](import-test-data).
