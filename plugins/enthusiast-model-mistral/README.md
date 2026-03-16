# Mistral AI Models

This Enthusiast plugin enables Mistral AI models for generating embeddings and LLMs.

## Installation

Run the following command inside your application directory:

```shell
pip install enthusiast-model-mistral
```

## Configuration

Register the providers in your `settings_override.py`:

```python
CATALOG_LANGUAGE_MODEL_PROVIDERS = [
    'enthusiast_model_mistral.MistralAILanguageModelProvider',
]

CATALOG_EMBEDDING_PROVIDERS = [
    'enthusiast_model_mistral.MistralAIEmbeddingProvider',
]
```

Set the required environment variable:

```
MISTRAL_API_KEY=<your_mistral_api_key>
```
