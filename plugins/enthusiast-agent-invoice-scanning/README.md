# Enthusiast Invoice Scanning Agent

The Invoice Scanning agent processes supplier invoices — PDFs, scanned images, or structured files — and extracts SKU and quantity data from each line item. It validates the extracted SKUs against the product catalog and, upon confirmation, updates stock levels directly in the configured e-commerce platform.

## Installing the Invoice Scanning Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-invoice-scanning
```

Then, register the agent in your `settings_override.py`:

```python
AVAILABLE_AGENTS = [
    'enthusiast_agent_invoice_scanning.InvoiceScanningAgent',
]
```

## Product Requirements (Medusa)

For invoice scanning to work correctly, each product variant in the e-commerce platform must have the following fields set to the **same value as its SKU**:

| Field | Purpose |
|---|---|
| `ean` | Used by `get_product_by_sku` to look up the product (Medusa filters products by `variants[ean][]`) |
| `sku` (variant) | Inherited by the auto-created inventory item at creation time — used by `_get_inventory_item_id_by_sku` to find the inventory item |
| `sku` (inventory item) | Queried directly via `GET /admin/inventory-items?sku=...` to resolve the inventory item for stock updates |

**Important:** Medusa does **not** propagate a variant `sku` change to an already-existing inventory item. If a product was created without `sku` set, the inventory item's `sku` must be patched directly via `POST /admin/inventory-items/{id}`.

`manage_inventory` defaults to `true` in the Medusa v2 admin API and does not need to be set explicitly.

### Seeding products

The `sample-invoices/seed_medusa_products.py` script creates or updates all sample products to satisfy the requirements above. Run it with:

```bash
MEDUSA_API_KEY=<your-key> python3 sample-invoices/seed_medusa_products.py
```
