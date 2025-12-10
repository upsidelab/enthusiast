CUSTOM_QUERY_PROMPT_TEMPLATE = """
    With the following database schema delimited by three backticks ```
    CREATE TABLE catalog_product (
        \"id\" int8 NOT NULL,
        \"entry_id\" varchar NOT NULL,
        \"name\" varchar NOT NULL,
        \"slug\" varchar NOT NULL,
        \"description\" text NOT NULL,
        \"sku\" varchar NOT NULL,
        \"properties\" jsonb NOT NULL,
        \"categories\" varchar[] NOT NULL,
        \"price\" float8 NOT NULL,
        PRIMARY KEY (\"id\")
    );```
    that contains product information, with some example values delimited by three backticks
    ```
    {sample_products_json}
    ```
    generate a JSON for Django ORM with parameters to Q() function that will be passed to filter(), exclude() and order_by() with corresponding keys:
    {{
        filter: json with params for Q() function that will be passed to filter() function, 
        exclude: json with params for Q() function that will be passed to exclude() function,
        order_by: list of order_by() arguments to sort results
    }}
    that can be useful when answering the following request delimited by three backticks.
    
    Rules:
    - Use only expressions that suits provided table definition
    - Use numeric comparison lookups (__lt, __gt, __lte, __gte) only on pure numeric fields (int, float) with numerical values only.
    - Respect Django rules for building lookup expression especially for JSON field and Array field.
    - Do not generate list membership (__in, __contains) lookups on JSON subkeys use multiple direct equality instead.
    - Possible logical operators are: AND, OR

    EXAMPLE:

    {{
        'filter': {{    
            'AND': [
                {{'<colum-name>__<django_lookup_expression>': <value>}},
                {{'<colum-name>__<django_lookup_expression>': <value>}}
            ],
            'OR': [
                {{'<colum-name>__<django_lookup_expression>': <value>}},
                {{'AND': [
                    {{'<colum-name>__<django_lookup_expression>': <value>}},
                    {{'<colum-name>__<django_lookup_expression>': <value>}}
                ]}}
            ]
        }},
        'exclude': {{    
            'AND': [
                {{'<colum-name>__<django_lookup_expression>': <value>}},
                {{'<colum-name>__<django_lookup_expression>': <value>}}
            ]
        }},
        'order_by': [<value>, <value>]
    }}
    Distinct columns values: {distinct_columns_values}
    ``` 
    {query} 
    ```
    Return only JSON
"""
