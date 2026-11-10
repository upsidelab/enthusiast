# Porting custom code from Enthusiast 1.7 to 2.0

This guide is for installations that changed Enthusiast 1.7: own plugins (sources, integrations, agents, tools), changes to the server, scripts that call the API, or a fork of the UI. It complements the upgrade guide, which covers migrating the database. Port your plugins before you install 2.0 (step 2 of the upgrade guide). Plugins built for 1.7 import `enthusiast-common`, so 2.0 can't load them.

## 1. Where custom code goes now

Enthusiast 2.0 runs on Suvereo. Suvereo is a domain-agnostic core: data sets, agents, conversations, agentic executions, integrations, users and permissions. Enthusiast is a domain definition installed on top of it, and supplies the e-commerce domain: the product and document models, the product and document sources, the e-commerce integration, and the agent builder that hands retrievers and the store connector to agents.

Your code goes in one of three places:

- **Your own plugins.** They depend on `suvereo-common` for core contracts, and on `enthusiast-domain-common` or `enthusiast-domain` for e-commerce ones. This is the recommended home, and the way most 1.7 plugins port.
- **The domain definition itself.** If you need to change the domain, for example by adding fields to products or embedding them (section 6), you can fork `enthusiast-domain` or add a Django app on top of it.
- **The core.** Changes to the server itself, such as new endpoints or permissions, need a fork of Suvereo. Keep them to a minimum, since every core upgrade has to be merged by hand.

## 2. Packages and imports

`enthusiast-common` is split in two. Core contracts move to `suvereo-common`, and e-commerce contracts move to `enthusiast-domain-common`. The shared agent packages are renamed or split along the same line:

| 1.7 package | 2.0 package |
|---|---|
| `enthusiast-common` | `suvereo-common` (core), `enthusiast-domain-common` (e-commerce) |
| `enthusiast-agent-tool-calling` | `suvereo-agent-tool-calling` |
| `enthusiast-agent-tools` | `suvereo-agent-tools` (file and execution tools), `enthusiast-domain-tools` (product tools) |
| `enthusiast-model-*` | `suvereo-model-*`. Class names and provider `NAME`s are unchanged. |
| (none) | `enthusiast-domain`: the domain definition's models, retrievers, sync managers, builder and injector |

Update your plugin's dependencies to match. Source and integration plugins usually need only `enthusiast-domain-common`. Agents that use the domain definition's builder, models or retrievers also need `enthusiast-domain`.

Imports move as follows:

| 1.7 import | 2.0 import |
|---|---|
| `enthusiast_common.{ProductSourcePlugin, DocumentSourcePlugin}`, `enthusiast_common.interfaces.ECommerceIntegrationPlugin` | `enthusiast_domain_common` |
| `enthusiast_common.{ProductDetails, DocumentDetails}`, `enthusiast_common.structures.{Address, ProductUpdateDetails}` | `enthusiast_domain_common.structures` |
| `enthusiast_common.connectors.ECommercePlatformConnector` | `enthusiast_domain_common.connectors` |
| `enthusiast_common.errors.{ECommerceConnectorError, RetrieverError}` | `enthusiast_domain_common.connectors.errors.ECommerceConnectorError`, `enthusiast_domain_common.errors.RetrieverError` |
| `enthusiast_common.{agents, builder, injectors, config, tools, llm, registry, repositories, retrievers, memory, callbacks, services, agentic_execution}` | the same module under `suvereo_common` |
| `enthusiast_common.structures.{TextContent, LLMFile, …}`, `RepositoriesInstances` | `suvereo_common.structures` |
| `enthusiast_common.utils.{RequiredFieldsModel, AgentAdditionalArguments, …}` | `suvereo_common.utils` |
| `enthusiast_agent_tool_calling.BaseToolCallingAgent` | `suvereo_agent_tool_calling.BaseToolCallingAgent` |
| `enthusiast_agent_tools.{FileListTool, FileRetrievalTool, StopExecutionTool}` | `suvereo_agent_tools` |
| `enthusiast_agent_tools.{ProductExamplesTool, ProductSQLSearchTool, UpsertProductDetailsTool, UpsertMemoryEntry}` | `enthusiast_domain_tools` |
| `catalog.models.{Product, Document, DocumentChunk}` (server) | `enthusiast_domain.models` |

Removed without a replacement: `BaseAgentConfigProvider`, `ConfigType`, `RetrieverConfig`, `RetrieversConfig`, `BaseProductRetriever`, `BaseProductRepository`, `BaseModelChunkRepository`, `DocumentChunkDetails`, `ProductContentChunk`, and `AgentAdditionalArguments.PROMPT_EXTENSION`. Sections 4–6 cover what replaces them.

## 3. Settings

Plugins are still registered by dotted path in `server/config/settings_override.py`. The domain definition is enabled there too:

| 1.7 setting | 2.0 setting |
|---|---|
| `AVAILABLE_AGENTS`, `AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS` | unchanged |
| `CATALOG_PRODUCT_SOURCE_PLUGINS`, `CATALOG_DOCUMENT_SOURCE_PLUGINS`, `CATALOG_ECOMMERCE_INTEGRATION_PLUGINS` | merged into `CATALOG_INTEGRATION_PLUGINS` |
| `CATALOG_LANGUAGE_MODEL_PROVIDERS`, `CATALOG_EMBEDDING_PROVIDERS` | unchanged, with paths renamed `enthusiast_model_*` → `suvereo_model_*` |
| (none) | `INSTALLED_DOMAIN_DEFINITIONS`: Django apps installed as domain definitions, merged into `INSTALLED_APPS` |
| (none) | `CATALOG_INTEGRATION_MANAGERS`: the classes that persist what integrations sync (section 4) |
| (none) | `CATALOG_ENTITY_PLUGINS`: the domain models that are listed in the UI and API |
| `CATALOG_MODELS` entries `product`, `product_chunk`, `document_chunk` | removed; the domain definition's models are imported directly |

```python
INSTALLED_DOMAIN_DEFINITIONS = ["enthusiast_domain"]

AVAILABLE_AGENTS = [
    "enthusiast_agent_product_search.ProductSearchAgent",
    "my_agent.MyAgent",
]
AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS = [...]

CATALOG_LANGUAGE_MODEL_PROVIDERS = ["suvereo_model_openai.OpenAILanguageModelProvider"]
CATALOG_EMBEDDING_PROVIDERS = ["suvereo_model_openai.OpenAIEmbeddingProvider"]

CATALOG_INTEGRATION_PLUGINS = [
    "enthusiast_source_medusa.MedusaIntegration",
    "my_source.MyProductSource",
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

## 4. Custom sources and integrations

Product sources, document sources and e-commerce integrations are now all integrations. Their base classes keep their names and move to `enthusiast_domain_common`, and all three build on `suvereo_common.integrations.BaseIntegration`. A plugin still only fetches. Storing what it returns is done by an integration manager from the domain definition, chosen by the plugin's base class: `ProductSourceManager` for product sources, and so on. A port therefore doesn't touch persistence.

What changes in a plugin class:

- **`TYPE` is new and required.** It's a stable slug, stored in the database to identify the plugin, for example `"my_store_product"`. Don't change it after the plugin is in use. When you upgrade a database, the mapping in the restore script must have a row with this `TYPE` for your plugin's 1.7 `plugin_name` (see the upgrade guide).
- **`NAME`** is unchanged. It's the name shown in the UI and is no longer stored.
- **`ALLOWS_MULTIPLE_INSTANCES` is new and optional,** defaulting to `True`: a data set can hold several integrations of the type, such as two stores on the same platform. Set it to `False` for a type that makes sense once per data set. If you allow several instances, override `instance_name()` to return something that tells them apart, such as the store's host.
- **The constructor no longer takes `data_set_id`**, and `self.data_set_id` doesn't exist. Plugins are instantiated with no arguments. If your source depended on the data set, move that into its configuration. An e-commerce integration's `build_product_source()` constructs its source without the argument too.
- **`CONFIGURATION_ARGS`** works as before: a `RequiredFieldsModel` (or any Pydantic model), whose instance is available as `self.CONFIGURATION_ARGS` at runtime. The configuration form in the UI is generated from it. The field types the form renders are text and, for enums, a select.
- **`fetch()`, `build_connector()` and `build_product_source()`** are unchanged, and so are `ProductDetails`, `DocumentDetails`, `ProductUpdateDetails`, `Address` and the `ECommercePlatformConnector` methods.

Stored configuration is no longer wrapped: 1.7 kept `{"configuration_args": {...}}`, and 2.0 keeps the settings object itself. This matters only to code that reads or writes the stored integration rows directly.

```python
# 1.7
from enthusiast_common import ProductDetails, ProductSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel


class MyStoreConfig(RequiredFieldsModel):
    api_url: str


class MyProductSource(ProductSourcePlugin):
    NAME = "My Store"
    CONFIGURATION_ARGS = MyStoreConfig

    def __init__(self, data_set_id):
        super().__init__(data_set_id)

    def fetch(self) -> list[ProductDetails]: ...


# 2.0
from enthusiast_domain_common import ProductDetails, ProductSourcePlugin
from suvereo_common.utils import RequiredFieldsModel


class MyProductSource(ProductSourcePlugin):
    TYPE = "my_store_product"
    NAME = "My Store"
    CONFIGURATION_ARGS = MyStoreConfig

    def fetch(self) -> list[ProductDetails]: ...
```

Register the plugin in `CATALOG_INTEGRATION_PLUGINS`. See Building a custom integration in the [Suvereo documentation](../../../../suvereo/docs/customization/domain-onboarding) for the full contract, including integrations that hand agents tools instead of syncing data.

## 5. Custom agents and tools

Tools need only their imports changed. The base classes, their constructors and `run()` are the same, and tools still reach data through `self._injector`. Agents change more, mainly because the config provider is gone and domain access moved to the domain definition's builder.

**The config provider is replaced by class attributes.**

- `BaseAgentConfigProvider` and `config.py` go. The agent declares its system prompt as `SYSTEM_PROMPT`, which is required.
- Where the provider returned a different prompt or different tools for agentic executions, set `SYSTEM_PROMPT` and `TOOLS` on the execution definition instead. `TOOLS` replaces the agent's tools for the execution, so list every tool it needs, for example `[*MyAgent.TOOLS, LLMToolConfig(tool_class=StopExecutionTool)]`. Leave it unset to keep the agent's tools.
- `CONVERSATION_HISTORY_TOKEN_LIMIT` is new. Leave it unset to use the server's `DEFAULT_CONVERSATION_HISTORY_TOKEN_LIMIT` (10,000 tokens). 1.7 tool-calling agents used a fixed 3,000.

**Domain access goes through the domain definition's builder.**

- In 2.0, the injector built by default carries only what every agent can use: repositories, chat history, memory and the tool scratchpad.
- `product_retriever`, `document_retriever` and `ecommerce_platform_connector` come from `enthusiast_domain.builder.EcommerceAgentBuilder`. An agent whose tools use them sets `BUILDER_CLASS = EcommerceAgentBuilder`, as all the built-in Enthusiast agents do.
- Sub-agents built through `AgentToolConfig` use their parent's builder.
- To customize a retriever, which 1.7 did through `RetrieversConfig`, subclass `EcommerceAgentBuilder` and override `_build_product_retriever` or `_build_document_retriever`. Then point `BUILDER_CLASS` at your builder. See [Agent types](/docs/agents/agent-types) and the [Suvereo injector documentation](../../../../suvereo/docs/agents/injector).

**Data access.**

- `repositories.product`, `repositories.product_chunk` and `repositories.document_chunk` are removed. Use the retrievers, or query `enthusiast_domain.models.Product`, `Document` and `DocumentChunk` directly.
- The products table is now `enthusiast_domain_product` (was `catalog_product`). Update prompts and tools that make the model write SQL against it.
- `BaseVectorStoreRetriever` takes `(data_set_id, embeddings_registry, searcher, max_objects)`. A subclass declares `chunk_model` and `dataset_filter`, and no longer implements the search unless it needs a custom strategy.
- `BaseEmbeddingProviderRegistry.provider_for_dataset()`, which returned a class, is now `provider_instance_for_dataset()`, which returns a ready instance.

**Agent configuration.**

- `agent_args`, `prompt_input` and `tools` keep their shape.
- `prompt_extension` is removed, and the upgrade strips it from stored agents. If you relied on it, move that text into `SYSTEM_PROMPT` or a `PROMPT_INPUT` field.
- `PROMPT_INPUT` fields are now available in the system prompt as `{field_name}` without overriding `_get_system_prompt_variables()`.
- A `Json` field such as `output_format` accepts a JSON string or an object.

**Smaller changes.**

- `AgentToolConfig(tool_class=..., agent=AgentConfig(...))` becomes `AgentToolConfig(tool_class=..., agent_class=MyAgent)`. The sub-agent's configuration comes from `MyAgent`'s class attributes.
- `ECommerceConnectorError` is a plain exception and no longer has `agent_friendly_message`. Code that caught it and read that property must build its own message.
- An agent that subclasses `BaseAgent` directly must implement `async aget_answer()`. Its constructor must also accept `conversation_history_token_limit` if overridden. An intermediate abstract base class must set `__abstract__ = True`, or it fails the check for `NAME`, `AGENT_KEY` and `SYSTEM_PROMPT` at import.

```python
# 1.7: agent.py and config.py
class MyAgent(BaseToolCallingAgent):
    AGENT_KEY = "my-agent"
    NAME = "My Agent"
    PROMPT_INPUT = MyPromptInput
    TOOLS = [LLMToolConfig(tool_class=UpsertProductDetailsTool)]


class MyAgentConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type=ConfigType.CONVERSATION):
        if config_type == ConfigType.CONVERSATION:
            return AgentConfigWithDefaults(system_prompt=CHAT_PROMPT, agent_class=MyAgent, tools=MyAgent.TOOLS)
        tools = MyAgent.TOOLS + [LLMToolConfig(tool_class=StopExecutionTool)]
        return AgentConfigWithDefaults(system_prompt=EXECUTION_PROMPT, agent_class=MyAgent, tools=tools)


# 2.0: agent.py and execution_definition.py
from enthusiast_domain.builder import EcommerceAgentBuilder
from suvereo_agent_tool_calling import BaseToolCallingAgent


class MyAgent(BaseToolCallingAgent):
    AGENT_KEY = "my-agent"
    NAME = "My Agent"
    SYSTEM_PROMPT = CHAT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    PROMPT_INPUT = MyPromptInput
    TOOLS = [LLMToolConfig(tool_class=UpsertProductDetailsTool)]


class MyAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    ...
    SYSTEM_PROMPT = EXECUTION_PROMPT
    TOOLS = [*MyAgent.TOOLS, LLMToolConfig(tool_class=StopExecutionTool)]
```

Agent keys, execution keys and the settings that register them are unchanged, so agents and executions stored in 1.7 keep pointing at the right classes. See [Building an agent](../../../../suvereo/docs/customization/tutorial/agent) for the full contract.

## 6. Product embeddings

1.7 chunked and embedded products on every sync, but none of its built-in agents read those embeddings: products are searched with SQL. 2.0 doesn't embed products, and the upgrade doesn't migrate product chunks. If one of your agents searched products by embedding, through `repositories.product_chunk` or `ProductContentChunk`, add product chunks back as follows, then re-sync your product sources to fill them.

The pieces mirror how 2.0 handles document chunks. The steps below change the domain definition directly, which suits a fork:

1. **A chunk model.** Subclass `suvereo_common.indexing.BaseEmbeddingChunk`, which provides `content` and `embedding`. Add a foreign key to the product with `related_name="chunks"`, which the indexer relies on. Then create a migration for it.

   ```python
   class ProductChunk(BaseEmbeddingChunk):
       product = models.ForeignKey("enthusiast_domain.Product", on_delete=models.CASCADE, related_name="chunks")
   ```

2. **The text to embed.** Add `get_indexable_content()` to `Product`. 1.7 embedded `f"{self.name} {self.description}"`.
3. **Chunking on sync.** In `ProductSourceManager.sync`, index each product after saving it: `product, _ = Product.objects.update_or_create(...)`, then `self._indexer.index(product)`. The indexer splits the text with the data set's chunk size and overlap, embeds the chunks with the data set's embedding model, and replaces the product's chunks. E-commerce integrations sync through `ProductSourceManager`, so they are covered too.
4. **A retriever.** Subclass `suvereo_common.retrievers.BaseVectorStoreRetriever` with `chunk_model = ProductChunk` and `dataset_filter = "product__dataset_id"`. Its `find_content_matching_query(query)` returns the closest chunks. 1.7's search by keyword and distance needs an override of that method.
5. **Wiring.** Add the retriever to `EcommerceInjector` as a property, and build it in `EcommerceAgentBuilder` the way `_build_document_retriever` builds the document retriever. Your tools then use `self._injector.product_chunk_retriever`, or whatever you named the property.

**Keeping the domain definition unmodified.** The same pieces can live in your own Django app instead. Install the app through `INSTALLED_DOMAIN_DEFINITIONS`, after `enthusiast_domain`. The differences:

- `Product` can't gain a method in place, so add `get_indexable_content()` on a proxy model of `Product`, and index instances of that proxy.
- Subclass `ProductSourceManager` to index the integration's products after `super().sync(...)`. `ECommerceIntegrationManager` creates a `ProductSourceManager` itself, so subclass it too, to use yours.
- List both subclasses in `CATALOG_INTEGRATION_MANAGERS`, in place of the domain definition's.
- Subclass `EcommerceInjector` and `EcommerceAgentBuilder`, and set your builder as `BUILDER_CLASS` on your agents.

**Filling the chunks.** After the upgrade, sync each product source and e-commerce integration once. Each sync re-embeds every product the source returns, which costs embedding API calls in proportion to the catalog. A sync runs as one background task, so a large catalog takes a while. Products that the source no longer returns are left without chunks.

## 7. Authorization in server code

This applies to custom endpoints and other code in the server or in a domain definition app. 2.0 replaces 1.7's admin flag and data-set membership with roles.

- **Admins are superusers.** 1.7 checked `is_staff`, mostly through DRF's `IsAdminUser`. 2.0 doesn't check `is_staff` anywhere. Admins are `is_superuser` users, and they pass every permission check.
- **Check permissions, not admin status.** An endpoint uses `permission_classes = [IsAuthenticated]` and a permission check from `account.authorization`. Use `global_permission_required(PERMISSIONS.X.Y)` for global resources. For resources in a data set, use `enforce_dataset_scoped_permission(...)`. It answers 404 to users with no access to the data set, so its existence isn't revealed, and 403 to members who lack the permission. For example:

  ```python
  class MyAgentReportView(APIView):
      permission_classes = [IsAuthenticated]

      def get(self, request, pk):
          agent = get_object_or_404(Agent, pk=pk)
          enforce_dataset_scoped_permission(self, PERMISSIONS.AGENT.VIEW, agent.dataset, obscured_model=Agent)
          ...
  ```

- **Reuse existing permission codes.** Roles can hold only the codes defined in core, such as `AGENT.VIEW`, `CONVERSATION.CONVERSE`, `AGENTIC_EXECUTION.CREATE` or `INTEGRATION.SYNC`. A plugin or domain definition can't register new grantable permissions. A new code is a core change.
- **Data-set membership is gone.** `DataSet.users`, `user.data_sets` and `User.has_dataset_access()` are removed. Their replacements:

  | Check | 2.0 helper |
  |---|---|
  | data sets a user can see | `datasets_visible_to(user)` |
  | data sets where a user holds a permission | `datasets_with_permission(user, code)` |
  | whether a user can see a data set | `is_dataset_member(user, data_set)` |
  | whether a user holds a permission on a data set | `has_dataset_perm(user, code, data_set)` |

  To grant access in code, assign a data-set role (`DatasetUserRoleAssignment`) instead of adding the user to the data set.
- **`User.groups` is gone.** Django's `auth.Group` is no longer linked to users. Groups are now `UserGroup` (`user.user_groups`). They carry no permissions themselves, only the roles assigned to them. Permissions granted directly to a user are ignored too.
- **Default managers hide internal rows.** `User.objects` excludes internal users, `DataSet.objects` excludes temporary data sets, and `Conversation.objects` excludes temporary conversations. Use `all_objects` where you need them.

## 8. API clients

Scripts and integrations that call the API need changes in three areas: authentication, permissions and a few endpoints.

**Authentication.** API keys of service accounts keep working, with the same `Authorization: Token <key>` header. That's the recommended way for programs to call the API (see the API documentation in Suvereo). Logging in as a user changed:

| | 1.7 | 2.0 |
|---|---|---|
| `POST /api/auth/login` with `{"email", "password"}` | `{"token"}`, a key that never expires | `{"access", "refresh"}`. The access token lasts 15 minutes, the refresh token 7 days. |
| Header | `Authorization: Token <token>` | `Authorization: Bearer <access>` |
| Refresh | (none) | `POST /api/auth/token/refresh` with `{"refresh"}` returns a new pair. The old refresh token stops working. |
| Logout | (none) | `POST /api/auth/logout` with `{"refresh"}` |
| Failed login | 403 | 401 |

Token lifetimes are set with `ECL_AUTH_ACCESS_TOKEN_TTL_SECONDS` and `ECL_AUTH_REFRESH_TOKEN_TTL_SECONDS`. A password change revokes the user's tokens.

**WebSocket.** Conversations stream over `ws/chat/<conversation_id>/`, as before, but the connection now needs authentication. Get a single-use ticket with `POST /api/auth/ws_ticket`, which returns `{"ticket"}` and expires after 10 seconds. Then connect to `ws/chat/<conversation_id>/?ticket=<ticket>`. Non-browser clients must also send an `Origin` header that's allowed in `ECL_DJANGO_CORS_ALLOWED_ORIGINS`.

**Permissions.** A service account is authorized through roles, like a user. A 1.7 key whose account relied on the staff flag or on data-set membership still authenticates, but gets 403 or 404 until its account is made an admin or granted roles.

**Endpoints.** Agents, conversations, agentic executions and data sets keep their URLs and payloads. Responses gain a few fields, such as `user_email` and a data set's `permissions`. Asking in a conversation now requires being its owner. The rest changed:

| 1.7 | 2.0 |
|---|---|
| `/api/data_sets/<id>/product_sources…`, `…/document_sources…`, `…/ecommerce_integration` | `/api/data_sets/<id>/integrations/` and `/api/data_sets/<id>/integrations/<pk>/`. Integration types are listed at `/api/integration-types/`. |
| `/api/sync`, `/api/data_sets/<id>/sync` and the per-source `…/sync` endpoints | `POST /api/data_sets/<id>/integrations/<pk>/sync/` returns `{"task_id"}`. There is no endpoint that syncs everything at once. |
| `GET /api/data_sets/<id>/products`, `…/documents` | `GET /api/data_sets/<id>/products/`, `…/documents/`. Each item has `id` plus the entity's listed fields: `name`, `sku` and `price` for products; `title` and `url` for documents. Entity types are listed at `/api/entities/`. |
| `/api/data_sets/<id>/users` | `/api/data_sets/<id>/roles/…` and `/api/data_sets/<id>/groups/…` |
| `GET /api/task_status/<task_id>/` | `GET /api/message-push-status/<task_id>/` |
| `GET /api/account` returns `is_staff` | returns `is_admin` and `permissions` |

Swagger at `/api/docs/` lists the full 2.0 API.

## 9. Frontend customizations

The 2.0 UI evolved from the 1.7 one rather than being rewritten, and it shares its history. The stack, build, `VITE_API_BASE` / `VITE_WS_BASE` variables, Tailwind theme, UI primitives and logo files are unchanged. 2.0 uses Node 22 and pnpm only.

The files a fork most likely touched were rewritten, though: routing (`main.tsx`), the sidebar, the API client and its authentication, and the shared types. Re-apply your changes on top of the 2.0 frontend rather than merging your fork. Expect conflicts in nearly every change except styling.

- **Products, documents and source pages are generic now.** The products and documents pages are replaced by an entity listing built from the server's entity metadata. The per-kind source pages are replaced by one integrations page, with configuration forms generated from each plugin's `CONFIGURATION_ARGS`. If you customized those pages, check whether the generic ones already cover what you need. Write frontend code only for what they don't, such as detail views or custom cell rendering.
- **API calls go through `authenticatedFetch`.** Custom API clients extend `BaseApiClient` and call `this.authenticatedFetch(url, init)`, which adds the access token and refreshes it. `_requestConfiguration()` and the `token` key in local storage are gone.
- **The UI checks permissions, not the staff flag.** `account.isStaff` is replaced by `isAdmin` and a list of permissions. Gate custom pages and actions with `RequirePermission`, `hasPermission` or `hasDataSetPermission` and the codes in `lib/permissions/codes.ts`.
- **Branding is still in the source.** The product name, logos and help links are in `index.html`, the login page, the data-set selector and the sidebar. Re-apply your changes there.
