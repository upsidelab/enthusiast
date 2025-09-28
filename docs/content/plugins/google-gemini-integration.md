---
sidebar_position: 7
---

# Google Gemini Integration

The Google plugin for Enthusiast, makes it possible to use Gemini models.

### Install the Plugin

First, install the `enthusiast-model-google` package using pip:

```shell
pip install enthusiast-model-google
```

### Generate API key
1. Navigate to https://aistudio.google.com/apikey
2. Log in.
3. Hit "Create API key" button in upper right corner.

### Set environment variable
```
GOOGLE_API_KEY=<your_gemini_api_key>
```

### Enable the relevant language model and embedding providers in the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_LANGUAGE_MODEL_PROVIDERS = {
    "Google": "enthusiast_model_google.GoogleLanguageModelProvider",
}

CATALOG_EMBEDDING_PROVIDERS = {
    "Google": "enthusiast_model_google.GoogleEmbeddingProvider",
}
```

Save the changes and restart the web server and the worker.

### Configuring a Data Set to use Google Gemini

After installing and configuring the plugin, you can now select Google Gemini as a language model and embedding provider when [setting up a new data set](/tools/enthusiast/docs/synchronize/manage-data-sets/#creating-a-data-set).
