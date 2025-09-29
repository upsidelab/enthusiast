---
sidebar_position: 6
---

# Azure OpenAI Integration

The Azure OpenAI plugin for Enthusiast, makes it possible to use OpenAI models hosted on Azure.

## Installing the Plugin

First, install the `enthusiast-model-azureopenai` package using pip:

```shell
potery add enthusiast-model-azureopenai
```

Then, enable the relevant language model and embedding providers in the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_LANGUAGE_MODEL_PROVIDERS = {
    "AzureOpenAI": "enthusiast_model_azureopenai.AzureOpenAILanguageModelProvider",
}

CATALOG_EMBEDDING_PROVIDERS = {
    "AzureOpenAI": "enthusiast_model_azureopenai.AzureOpenAIEmbeddingProvider",
}
```

Save the changes and restart the web server and the worker.

## Configuring a Data Set to use Azure OpenAI

After installing and configuring the plugin, you can now select Azure OpenAI as a language model and embedding provider when [setting up a new data set](/docs/synchronize/manage-data-sets/#creating-a-data-set).
