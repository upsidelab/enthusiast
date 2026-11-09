# Try It Out

Once the test data set has been imported and indexed, you can start chatting with an agent. This guide uses the **Product Search** agent, which you installed in the [installation guide](/docs/getting-started/installation). It searches the product catalog and asks follow-up questions to narrow down the results.

## Creating the Agent

An agent type registered in `AVAILABLE_AGENTS` becomes available in the admin UI, where you create agents of that type for your data set.

In the left sidebar, go to "Configure" → "Agents" and add a new agent. Select **Product Search** as its type, give it a name and click "Create". The agent now appears in the sidebar under "Ask". Click it to open the chat.

## Sample Requests

The sample data set contains home internet and mobile plans. Here are a few requests to try:

> "I'm looking for a home internet plan with at least 100 Mb/s and premium TV channels."

> "Which mobile plans support 5G?"

> "What's the cheapest home internet plan with a 12-month contract?"

> "I need an internet connection for my office, with two landline phone lines."

The sample data set also contains documents, such as the TV channel list and the roaming charges policy. To ask questions about them, install the [User Manual Search](/agents/user-manual-search) agent, for example:

> "Will I get roaming charges if I go to Switzerland with the MobileUp Unlimited plan?"

## Next Steps

- [Learn more about data sets](../../../../suvereo/docs/management/data-sets)
- [See how to manage users](../../../../suvereo/docs/management/users)
- [Learn how e-commerce agents work](/docs/agents/agent-types)
- [Build your custom agent](/docs/customization/concept-product-search)
- [View available integrations](/integrations/)
- [Create a custom integration](../../../../suvereo/docs/customization/integrations)
