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
  price: number;
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
  configuration_args: Record<string, ExtraArgDetail>;
};

export type Agent = {
  id: number;
  name: string;
  description: string;
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
  is_execution_conversation: boolean;
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

export type TypeInfo = {
  container: string | null;
  inner_type?: string;
  key_type?: string;
  value_type?: string;
  nullable?: boolean;
};

export type ExtraArgDetail = {
  type: TypeInfo;
  description?: string | null;
  title?: string | null;
};

export type AgentConfig = {
  agent_args?: Record<string, ExtraArgDetail>;
  prompt_input?: Record<string, ExtraArgDetail>;
  prompt_extension?: Record<string, ExtraArgDetail>;
  tools?: Array<Record<string, ExtraArgDetail>>;
};

export type ConversationFile = {
  id: number;
  filename: string;
  file_url: string;
  content_type: string;
};

export type AgentExecution = {
  id: number;
  agent: number;
  execution_key: string;
  conversation: number;
  status: 'pending' | 'in_progress' | 'finished' | 'failed';
  input: Record<string, unknown>;
  result: Record<string, unknown> | null;
  failure_code: string | null;
  failure_explanation: string | null;
  celery_task_id: string | null;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
};

export type AgentExecutionDetail = AgentExecution & {
  files: ConversationFile[];
};

export type ExecutionType = {
  key: string;
  name: string;
  description: string | null;
  input_schema: Record<string, unknown>;
};

export type ToolStep = {
  name: string;
  done: boolean;
  errored?: boolean;
};

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
