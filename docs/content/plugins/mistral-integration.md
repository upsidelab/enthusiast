---
sidebar_position: 6
---

# MistralAI Integration

The MistralAI plugin for Enthusiast, makes it possible to use MistralAI models.

## Installing the Plugin

First, install the `enthusiast-model-mistral` package using pip:

```shell
potery add enthusiast-model-mistral
```

Then, enable the relevant language model and embedding providers in the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_LANGUAGE_MODEL_PROVIDERS = {
    "Mistral": "enthusiast_model_mistral.MistralAILanguageModelProvider",
}

CATALOG_EMBEDDING_PROVIDERS = {
    "Mistral": "enthusiast_model_mistral.MistralAIEmbeddingProvider",
}
```

Save the changes and restart the web server and the worker.

## Configuring a Data Set to use Azure OpenAI

After installing and configuring the plugin, you can now select Mistral as a language model and embedding provider when [setting up a new data set](/docs/synchronize/manage-data-sets/#creating-a-data-set).
