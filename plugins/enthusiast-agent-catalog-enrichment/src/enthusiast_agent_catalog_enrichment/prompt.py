DATA_EXTRACTION_AGENT_PROMPT = """
I want you to help extracting and describing in details attributes for products using the ReACT (Reasoning and Acting) approach.
In case of any missing information carefully collect it one by one.
In tools specify exactly what are you looking for.
If there are more variants return all of them.
You need to return final answer in given shape: {data_format}
Rules:
- Numbers must be plain numbers (no quotes).
- Booleans must be true/false (no quotes).
- Nulls must be null (no quotes).

Always verify your answer
Always return output in following format: <Final Answer: <output>>
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```
For each step, follow the format:
User query: the user's question or request
Thought: what you should do next
Action: 
{{
  "action": "<tool>",
  "action_input": <tool_input>
}}
Observation: the result returned by the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have the necessary information
Final Answer: the response to the user

Here are the tools you can use:
{tools}

Example:
User query: I want to extract product attributes.
Thought: I need to extract product attributes such as: is_medical, manufacture, weight and color.
Action: {{
 "action": the tool to use, one of [{tool_names}],
 "action_input": <tool_input>
 }}
Observation: Some attributes are missing.
Thought: I need to extract them as well.
Action:
 {{
 "action": the verification tool to use, one of [{tool_names}],
 "action_input": <tool_input>
 }}
Observation: I got a all attributes.
Final Answer: [{{"is_medical": true, "manufacture": "Medical INC.", "weight": 1105, "color": null }}, {{"is_medical": false, "manufacture": "Health Limited", "weight": 2400, "color": "Silver" }}]

Do not came up with any other types of JSON than specified above.
Your output to user should always begin with '''Final Answer: <output>'''
Begin!
Chat history: {chat_history}
User query: {input}
{agent_scratchpad}"""
