CUSTOM_QUERY_PROMPT_TEMPLATE = """
    With the following database schema delimited by three backticks ```
    CREATE TABLE catalog_product (
        \"id\" int8 NOT NULL,
        \"entry_id\" varchar NOT NULL,
        \"name\" varchar NOT NULL,
        \"slug\" varchar NOT NULL,
        \"description\" text NOT NULL,
        \"sku\" varchar NOT NULL,
        \"properties\" varchar NOT NULL,
        \"categories\" varchar NOT NULL,
        \"price\" float8 NOT NULL,
        PRIMARY KEY (\"id\")
    );```
    that contains product information, with some example values delimited by three backticks
    ```
    {sample_products_json}
    ```
    generate a where clause for an SQL query for fetching products that can be useful when answering the following 
    request delimited by three backticks.
    try to avoid using AND in queries so you get more results instead try with OR.
    try to place multiple like queries with different phrases.
    try to place a single words in LIKE queries so you can find more products.
    Make sure that the queries are case insensitive 
    ``` 
    {query} 
    ```
    Respond with the where portion of the query only, don't include any other characters, 
    skip initial where keyword, skip order by clause.
"""
