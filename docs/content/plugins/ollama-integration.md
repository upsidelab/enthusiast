---
sidebar_position: 6
---

# Ollama Integration

The Ollama plugin for Enthusiast, makes it possible to use self-hosted models provided via Ollama.

## Installing the Plugin

First, install the `enthusiast-model-ollama` package using pip:

```shell
pip install enthusiast-model-ollama
```

Then, enable the relevant language model and embedding providers in the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_LANGUAGE_MODEL_PROVIDERS = {
    "Ollama": "enthusiast_model_ollama.OllamaLanguageModelProvider",
}

CATALOG_EMBEDDING_PROVIDERS = {
    "Ollama": "enthusiast_model_ollama.OllamaEmbeddingProvider",
}
```

Save the changes and restart the web server and the worker.

## Configuring a Data Set to use Ollama

After installing and configuring the plugin, you can now select Ollama as a language model and embedding provider when [setting up a new data set](/tools/enthusiast/docs/synchronize/manage-data-sets/#creating-a-data-set).
