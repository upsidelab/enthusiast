export interface PaginatedResult<T> {
  results: T[];
  count: number;
}

export type DataSet = {
  id: number | undefined;
  name: string;
  languageModelProvider: string;
  languageModel: string;
  embeddingProvider: string;
  embeddingModel: string;
  embeddingVectorSize: number;
}

export type Product = {
  id: number;
  name: string;
  sku: string;
  slug: string;
  description: string;
  categories: string;
  properties: string;
}

export type CatalogSource = {
  id: number;
  plugin_name: string;
  config: string;
  data_set_id: number;
  corrupted: boolean;
}

export type Document = {
  id: number;
  url: string;
  title: string;
  content: string;
  isIndexed: boolean;
}

export type Account = {
  email: string;
  isStaff: boolean;
}

export type User = {
  id: number;
  email: string;
  isActive: boolean;
  isStaff: boolean;
}

export type SourcePlugin = {
  name: string;
  configuration_args: import("@rjsf/utils").RJSFSchema;
  $defs?: Record<string, import("@rjsf/utils").RJSFSchema>;
};

export type Agent = {
  id: number;
  name: string;
  agent_type: string;
  created_at: string;
  updated_at: string;
  deleted_at: string;
  corrupted: boolean;
};

export type Conversation = {
  id: number;
  started_at: Date;
  model: string;
  dimensions: number;
  data_set: string;
  summary?: string;
  agent: Agent;
  history?: Message[];
}

export type Message = {
  id: number;
  type: string;
  text: string;
}

export type ServiceAccount = {
  id: number;
  email: string;
  isActive: boolean;
  isStaff: boolean;
  dateCreated: string;
  dataSetIds: number[];
};

export type ProvidersConfig = {
  languageModelProviders: string[];
  embeddingProviders: string[];
}

export type AgentConfig = {
  agent_args?: Record<string, unknown>;
  prompt_input?: Record<string, unknown>;
  prompt_extension?: Record<string, unknown>;
  tools?: Record<string, unknown>[];
};

export const AGENT_CONFIG_SECTION_KEYS = ["agent_args", "prompt_input", "prompt_extension"] as const;
export type AgentConfigSectionKey = (typeof AGENT_CONFIG_SECTION_KEYS)[number];

export type AgentDetails = {
  id: number;
  name: string;
  description: string;
  file_upload: boolean;
  config: AgentConfig;
  dataset: number;
  agent_type: string;
  created_at: string;
  updated_at: string;
};
