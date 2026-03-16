# OpenAI Models

This Enthusiast plugin enables OpenAI models for generating embeddings and LLMs.

## Installation

Run the following command inside your application directory:

```shell
pip install enthusiast-model-openai
```

## Configuration

Register the providers in your `settings_override.py`:

```python
CATALOG_LANGUAGE_MODEL_PROVIDERS = [
    'enthusiast_model_openai.OpenAILanguageModelProvider',
]

CATALOG_EMBEDDING_PROVIDERS = [
    'enthusiast_model_openai.OpenAIEmbeddingProvider',
]
```

Set the required environment variable:

```
OPENAI_API_KEY=<your_openai_api_key>
```
