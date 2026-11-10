# Upgrading from Enthusiast 1.7 to 2.0

Enthusiast 2.0 runs on Suvereo: Suvereo is the core, and the e-commerce features come from the Enthusiast domain definition installed on top of it. You upgrade by migrating your 1.7 database in place. Most data keeps its IDs: users, data sets, agents, conversations, files, agentic executions and API keys.

Plan for the following:

- **Everyone logs in again.** Sessions are not carried over. API keys keep working.
- **Non-admin users lose access to data sets** until you grant them roles (step 6).
- **Users with the staff flag but no superuser flag are no longer admins** (step 6).
- **Product embeddings are not migrated.** None of the built-in agents use them, since they search products with SQL. If your own agents do, see [Product embeddings](/docs/migration/code-migration#6-product-embeddings) in the code migration guide. Document embeddings are kept as they are.

## Before you start

- Your 1.7 installation is on the latest 1.7 release, with all its migrations applied.
- You can run SQL against its database.
- You can run Django management commands with the 2.0 code, connected to that database.
- If you customized 1.7, for example with your own plugins, changes to the server or UI, or scripts that call the API, you've ported that code with the [code migration guide](/docs/migration/code-migration).

## 1. Back up the database

Stop the 1.7 application, including its workers, so nothing writes to the database during the upgrade. Then back up the database with your usual tooling, such as `pg_dump` or a snapshot from your provider. The upgrade changes the database in place. To roll back, restore the backup and start 1.7 again.

## 2. Install and configure 2.0

Replace your 1.7 deployment with Suvereo, whether it runs from the codebase or from Docker images. That covers the server, the workers and the frontend. Install the `enthusiast-domain` package and the agent, source and model plugins you use. The model plugins are renamed from `enthusiast-model-*` to `suvereo-model-*`. Don't start the application until the migrations in step 4 have run.

If you wrote your own plugins for 1.7, install the versions you ported to 2.0 (see the [code migration guide](/docs/migration/code-migration)).

In `server/config/settings_override.py`, enable the domain definition and carry over the plugins your 1.7 installation used:

| 1.7 setting | 2.0 setting |
|---|---|
| `AVAILABLE_AGENTS`, `AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS` | unchanged |
| `CATALOG_PRODUCT_SOURCE_PLUGINS`, `CATALOG_DOCUMENT_SOURCE_PLUGINS`, `CATALOG_ECOMMERCE_INTEGRATION_PLUGINS` | merged into `CATALOG_INTEGRATION_PLUGINS` |
| `CATALOG_LANGUAGE_MODEL_PROVIDERS`, `CATALOG_EMBEDDING_PROVIDERS` | unchanged, but the packages are renamed: `enthusiast_model_*` → `suvereo_model_*` |
| (none) | new: `INSTALLED_DOMAIN_DEFINITIONS`, `CATALOG_INTEGRATION_MANAGERS`, `CATALOG_ENTITY_PLUGINS` |

Register every model provider your data sets use, not only the default. A data set set to a provider that isn't registered can't run its agents. For example:

```python
INSTALLED_DOMAIN_DEFINITIONS = ["enthusiast_domain"]

AVAILABLE_AGENTS = [...]                           # as in 1.7
AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS = [...]    # as in 1.7

CATALOG_LANGUAGE_MODEL_PROVIDERS = [
    "suvereo_model_openai.OpenAILanguageModelProvider",
    "suvereo_model_anthropic.AnthropicLanguageModelProvider",
]
CATALOG_EMBEDDING_PROVIDERS = [
    "suvereo_model_openai.OpenAIEmbeddingProvider",
]

CATALOG_INTEGRATION_PLUGINS = [
    "enthusiast_source_sample.SampleProductSource",
    "enthusiast_source_sample.SampleDocumentSource",
    "enthusiast_source_medusa.MedusaIntegration",
]
CATALOG_INTEGRATION_MANAGERS = [
    "enthusiast_domain.sync.ProductSourceManager",
    "enthusiast_domain.sync.DocumentSourceManager",
    "enthusiast_domain.sync.ECommerceIntegrationManager",
]
CATALOG_ENTITY_PLUGINS = [
    "enthusiast_domain.models.Product",
    "enthusiast_domain.models.Document",
]
```

## 3. Set aside the data that the migrations move

The 2.0 migrations drop the 1.7 tables for products, documents, sources and data-set membership. Copy them aside first:

```sql
CREATE SCHEMA legacy_17;
CREATE TABLE legacy_17.catalog_product               AS TABLE public.catalog_product;
CREATE TABLE legacy_17.catalog_document              AS TABLE public.catalog_document;
CREATE TABLE legacy_17.catalog_documentchunk         AS TABLE public.catalog_documentchunk;
CREATE TABLE legacy_17.catalog_productsource         AS TABLE public.catalog_productsource;
CREATE TABLE legacy_17.catalog_documentsource        AS TABLE public.catalog_documentsource;
CREATE TABLE legacy_17.catalog_ecommerceintegration  AS TABLE public.catalog_ecommerceintegration;
CREATE TABLE legacy_17.catalog_dataset_users         AS TABLE public.catalog_dataset_users;
CREATE TABLE legacy_17.account_user_groups           AS TABLE public.account_user_groups;
```

## 4. Run the migrations

```sh
python manage.py migrate
```

## 5. Restore integrations, products and documents

First, list your 1.7 sources:

```sql
SELECT 'catalog_productsource' AS source_table, plugin_name, count(*) FROM legacy_17.catalog_productsource GROUP BY plugin_name
UNION ALL SELECT 'catalog_documentsource', plugin_name, count(*) FROM legacy_17.catalog_documentsource GROUP BY plugin_name
UNION ALL SELECT 'catalog_ecommerceintegration', plugin_name, count(*) FROM legacy_17.catalog_ecommerceintegration GROUP BY plugin_name
ORDER BY 1, 2;
```

Then save the script below as `restore_17.sql`. Each source from the list must appear in the mapping at its top. The mapping covers every official 1.7 source. For a custom source, add a row with its 2.0 `TYPE` and its `ALLOWS_MULTIPLE_INSTANCES` value (see [Custom sources and integrations](/docs/migration/code-migration#4-custom-sources-and-integrations)).

```sql
-- restore_17.sql
-- 1. Mapping of (1.7 table, plugin_name) -> 2.0 type and multi-instance flag.
--    Add a row here for any custom 1.7 source before running.
CREATE TEMP TABLE legacy_17_type_map (
    source_table              text    NOT NULL,
    plugin_name               text    NOT NULL,
    type                      text    NOT NULL,
    allows_multiple_instances boolean NOT NULL,
    PRIMARY KEY (source_table, plugin_name)
) ON COMMIT DROP;

INSERT INTO legacy_17_type_map VALUES
    ('catalog_productsource',        'Sample Product Source',  'sample-product',  false),
    ('catalog_documentsource',       'Sample Document Source', 'sample-document', false),
    ('catalog_ecommerceintegration', 'Medusa',                 'medusa',          true),
    ('catalog_productsource',        'Medusa',                 'medusa_product',  true),
    ('catalog_productsource',        'Shopify',                'shopify',         true),
    ('catalog_productsource',        'Shopware',               'shopware',        true),
    ('catalog_productsource',        'Solidus',                'solidus',         true),
    ('catalog_productsource',        'WooCommerce',            'woocommerce',     true),
    ('catalog_documentsource',       'WordPress',              'wordpress',       true),
    ('catalog_documentsource',       'Sanity CMS',             'sanity-cms',      true);

CREATE TEMP VIEW legacy_17_sources AS
          SELECT 'catalog_productsource'        AS source_table, id, plugin_name, config, data_set_id FROM legacy_17.catalog_productsource
UNION ALL SELECT 'catalog_documentsource',                       id, plugin_name, config, data_set_id FROM legacy_17.catalog_documentsource
UNION ALL SELECT 'catalog_ecommerceintegration',                 id, plugin_name, config, data_set_id FROM legacy_17.catalog_ecommerceintegration;

-- 2. Fail, naming them, if any 1.7 source has no mapping.
DO $$
DECLARE unmapped text;
BEGIN
    SELECT string_agg(DISTINCT s.source_table || ': ' || s.plugin_name, ', ')
      INTO unmapped
      FROM legacy_17_sources s
      LEFT JOIN legacy_17_type_map m USING (source_table, plugin_name)
     WHERE m.type IS NULL;
    IF unmapped IS NOT NULL THEN
        RAISE EXCEPTION 'Unmapped 1.7 plugin_name(s): %. Add them to legacy_17_type_map.', unmapped;
    END IF;
END $$;

-- 3. Integrations. Single-instance types keep only the lowest 1.7 id per data set.
INSERT INTO catalog_integration (type, config, created_at, updated_at, dataset_id, allows_multiple_instances)
SELECT m.type,
       COALESCE(s.config -> 'configuration_args', '{}'::jsonb),
       now(), now(),
       s.data_set_id,
       m.allows_multiple_instances
  FROM legacy_17_sources s
  JOIN legacy_17_type_map m USING (source_table, plugin_name)
 WHERE m.allows_multiple_instances
    OR s.id = (SELECT min(s2.id) FROM legacy_17_sources s2
                WHERE s2.source_table = s.source_table
                  AND s2.plugin_name  = s.plugin_name
                  AND s2.data_set_id  = s.data_set_id)
 ORDER BY s.data_set_id, s.source_table, s.id;

-- 4. Products and documents, keeping their ids. integration_id stays NULL until the next sync.
INSERT INTO enthusiast_domain_product
       (id, entry_id, name, slug, description, sku, properties, categories, price, dataset_id, integration_id)
SELECT  id, entry_id, name, slug, description, sku, properties, categories, price, data_set_id, NULL
  FROM legacy_17.catalog_product;

INSERT INTO enthusiast_domain_document (id, url, title, content, dataset_id, integration_id)
SELECT id, url, title, content, data_set_id, NULL
  FROM legacy_17.catalog_document;

-- 5. Document chunks, embeddings copied as-is.
INSERT INTO enthusiast_domain_documentchunk (id, content, embedding, document_id)
SELECT id, content, embedding, document_id
  FROM legacy_17.catalog_documentchunk;

-- 6. Move the identity sequences past the restored ids.
SELECT setval(pg_get_serial_sequence('enthusiast_domain_product', 'id'),
              COALESCE((SELECT max(id) FROM enthusiast_domain_product), 0) + 1, false);
SELECT setval(pg_get_serial_sequence('enthusiast_domain_document', 'id'),
              COALESCE((SELECT max(id) FROM enthusiast_domain_document), 0) + 1, false);
SELECT setval(pg_get_serial_sequence('enthusiast_domain_documentchunk', 'id'),
              COALESCE((SELECT max(id) FROM enthusiast_domain_documentchunk), 0) + 1, false);
```

Run `restore_17.sql` in a single transaction that stops at the first error. With `psql`, for example:

```sh
psql -v ON_ERROR_STOP=1 -1 -f restore_17.sql
```

If a source isn't mapped, the script stops, names it, and changes nothing.

## 6. Review admins and grant data-set access

**Admins.** 2.0 treats only superusers as admins. List the 1.7 admins who would lose admin rights:

```sql
SELECT email FROM account_user WHERE is_staff AND NOT is_superuser;
```

For each of them, either make them an admin (`UPDATE account_user SET is_superuser = true WHERE email IN (...);`) or grant them roles instead. Admins hold every permission, including managing other admins, so decide one by one.

**Data-set access.** 1.7 data-set membership doesn't carry over to the 2.0 permission system on its own. In 1.7, a member of a data set had full control of it: its agents, integrations and agentic executions. In 2.0, access to a data set comes from data-set roles, each a chosen set of permissions. Until you grant roles, non-admin users can't see their data sets.

2.0 ships with starter roles. Create them with:

```sh
python manage.py seedroles
```

Two of the starter data-set roles together match a 1.7 membership:

| Data-set role | Grants |
|---|---|
| Agent Interaction | Talking to the data set's agents and running agentic executions |
| Management | Configuring the data set's agents and integrations, and running syncs |

Grant roles in the UI, or restore every 1.7 membership as both roles with the script below. It reads the memberships you set aside in step 3, skips admins, and is safe to re-run.

```sql
INSERT INTO account_datasetuserroleassignment (user_id, dataset_id, role_id)
SELECT m.user_id, m.dataset_id, r.id
FROM legacy_17.catalog_dataset_users m
JOIN account_user u ON u.id = m.user_id AND NOT u.is_superuser
JOIN account_datasetrole r ON r.name IN ('Agent Interaction', 'Management')
ON CONFLICT (user_id, dataset_id, role_id) DO NOTHING;
```

**Groups.** 1.7 groups are not migrated. If you used them, recreate them in 2.0 as user groups and assign roles to them.

## 7. Copy uploaded files

2.0 must be able to reach the files uploaded to 1.7 conversations, at the same paths. If 2.0 uses the same file storage as 1.7, there's nothing to do. Otherwise, copy the files over and keep their paths.

## 8. Re-sync Sanity CMS and Shopify sources

These two sources got bug fixes in 2.0. If you use either, sync it once so its content is refreshed. Re-syncing Sanity CMS also re-embeds its documents, which costs embedding API calls.

## 9. Verify

- Products, documents and document chunks in 2.0 match the counts in `legacy_17`.
- As a non-admin user: log in, open a conversation, and search for a product and a document.
- Run an agentic execution on a migrated data set.

## 10. Clean up

Once everything works, drop the set-aside tables:

```sql
DROP SCHEMA legacy_17 CASCADE;
```

Integration settings, including API keys, are stored in plain text, as they were in 1.7. Until you drop it, `legacy_17` holds another copy of them. Protect the 1.7 backup from step 1 as you would the live database.
