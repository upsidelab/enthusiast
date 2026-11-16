# Enthusiast Domain

The e-commerce domain definition for [Suvereo](https://github.com/upsidelab/suvereo): a Django app providing the `Product` and `Document` models (with pgvector embeddings) and migrations, retrievers, sync managers, and the agent builder and injector.

## Installing

```commandline
poetry add enthusiast-domain
```

Then, register it in your config/settings_override.py.

```python
INSTALLED_DOMAIN_DEFINITIONS = [
    'enthusiast_domain',
]
```
