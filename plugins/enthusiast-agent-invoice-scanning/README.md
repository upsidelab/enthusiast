# Enthusiast Invoice Scanning Agent

The Invoice Scanning agent extracts attributes from invoices. It can be customized to pull different attribute sets and can flag unclear or missing information, triggering a human-in-the-loop step when clarification is required.

## Installing the Invoice scanning Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-invoice-scanning
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    "enthusiast_agent_invoice_scanning.InvoiceScanningAgent"
]
```