# Ollama Models

This Enthusiast plugin enables locally hosted models via Ollama for generating embeddings and LLMs.

## Installation

Run the following command inside your application directory:

```shell
pip install enthusiast-model-ollama
```

## Configuration

Register the providers in your `settings_override.py`:

```python
CATALOG_LANGUAGE_MODEL_PROVIDERS = [
    'enthusiast_model_ollama.OllamaLanguageModelProvider',
]

CATALOG_EMBEDDING_PROVIDERS = [
    'enthusiast_model_ollama.OllamaEmbeddingProvider',
]
```

The following environment variables are optional:

```
OLLAMA_HOST=http://127.0.0.1:11434  # defaults to http://127.0.0.1:11434 if not set
OLLAMA_API_KEY=<your_ollama_api_key>  # only required if your Ollama instance requires authentication
```
