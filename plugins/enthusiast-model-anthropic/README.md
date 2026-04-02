# Anthropic Models

This Enthusiast plugin enables Anthropic Claude models as LLMs.

Note: Anthropic does not provide an embeddings API, so this plugin must be used alongside another LLM provider that supports embeddings (Anthropic models handle agent chat conversations, while the other provider handles embedding calculations).

## Installation

Run the following command inside your application directory:

```shell
pip install enthusiast-model-anthropic
```

## Configuration

Register the provider in your `settings_override.py`:

```python
CATALOG_LANGUAGE_MODEL_PROVIDERS = [
    'enthusiast_model_anthropic.AnthropicLanguageModelProvider',
]
```

Set the required environment variable:

```
ANTHROPIC_API_KEY=<your_anthropic_api_key>
```
