# Enthusiast Order Intake Agent

The Order Intake agent converts handwritten notes, scans, and filled purchase-order PDFs into structured orders created directly in your e-commerce system. It can also detect when the provided input is incomplete or unclear; in those cases, it initiates a human-in-the-loop clarification step to confirm missing details before creating the order.

## Installing the Order Intake Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-order-intake
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    'enthusiast_agent_order_intake.OrderIntakeAgent',
]
```
