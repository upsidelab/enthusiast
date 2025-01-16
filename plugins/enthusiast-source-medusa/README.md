# Enthusiast Source Medusa E-Commerce Platform

This Enthusiast plugin enables the import of product data from Medusa.

# Usage
Assumption:
Medusa store is installed at http://localhost:9000/

Fetch products using below commands:
```
from source import MedusaProductSource                                                                                                                                                                                                                                                                       
s = MedusaProductSource(1, {"base_url": "http://localhost:9000/", "api_key": "your-jwt-token-here"})
s.fetch()
```