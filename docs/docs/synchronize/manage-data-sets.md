---
sidebar_position: 1
---

# Managing Data Sets


A Data Set is the top-level abstraction in Enthusiast. It represents a collection of products and documents and allows users to run agent requests on it. Data sets are isolated, meaning the agent will only use data from the specified data set in a request. You can also restrict access to data sets by user or service account.

While a single data set is usually enough to get started, there are scenarios where additional data sets can be useful, such as:

- **Multi-brand ecommerce:** Managing multiple brands within a single Enthusiast deployment.
- **Experimentation:** Testing different models and configurations
- **Content language separation:** Creating data sets per language to improve response accuracy.

## Creating a Data Set

1. Sign in as an admin user. In the left sidebar, go to “Manage” → “Data Sets” and click “New” at the top-right corner of the page.
2. Provide the following information:
  - **Name:** The display name of the data set.
  - **Embedding Provider:** The plugin for generating content embeddings (default: OpenAI).
  - **Embedding Model:** The model used for embeddings (default: large).
  - **Embedding Vector Size:** The size of the embeddings vector (default: 512).
3. Click "Create" at the bottom. 

Now, you're ready to connect your [data sources](/tools/enthusiast/docs/synchronize/connect-product-source).

## Assigning Users to a Data Set

1. Sign in as an admin user and go to “Manage” → “Data Sets”.
2. Locate the desired Data Set in the list and click “Manage Access” next to it.
3. Select the users and service accounts that should have access.
