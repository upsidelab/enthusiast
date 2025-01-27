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
  plugin_name: string;
} 

export type Conversation = {
  id: number;
  started_at: Date;
  model: string;
  dimensions: number;
  data_set: string;
  name?: string;
  history?: Message[];
}

export type Message = {
  id: number;
  role: string;
  text: string;
}

export type ServiceAccount = {
  id: number;
  email: string;
  isActive: boolean;
  dateCreated: string;
  dataSetIds: number[];
};

export type ProvidersConfig = {
  languageModelProviders: string[];
  embeddingProviders: string[];
}
