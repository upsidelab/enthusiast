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
