DATA_EXTRACTION_TOOL_CALLING_AGENT_PROMPT = """
I want you to help extracting and describing in details attributes for products.
In case of any missing information carefully collect it one by one.
In tools specify exactly what are you looking for.
If there are more variants return all of them.
You need to return variant data in given shape: {data_format}.
Always verify your answer
Return only json
"""
