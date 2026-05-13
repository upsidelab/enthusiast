import { BaseApiClient } from "@/lib/api/base.ts";
import { EmbeddingModelsConfig, ProvidersConfig } from "@/lib/types.ts";

type ProvidersConfigResponse = {
  language_model_providers: string[];
  embedding_providers: string[];
};

type EmbeddingModelsConfigResponse = {
  models: string[];
  vector_size_constraints: Record<string, number[]>;
};

export class ConfigApiClient extends BaseApiClient {
  async getAvailableProviders(): Promise<ProvidersConfig> {
    const response = await fetch(`${this.apiBase}/api/config`, this._requestConfiguration());
    const result = await response.json() as ProvidersConfigResponse;

    return {
      embeddingProviders: result.embedding_providers,
      languageModelProviders: result.language_model_providers
    };
  }

  async getLanguageModelsForProvider(name: string): Promise<string[]> {
    const response = await fetch(`${this.apiBase}/api/config/language_model_providers/${name}`, this._requestConfiguration());
    return await response.json() as string[];
  }

  async getEmbeddingModelsForProvider(name: string): Promise<EmbeddingModelsConfig> {
    const response = await fetch(`${this.apiBase}/api/config/embedding_providers/${name}`, this._requestConfiguration());
    const result = await response.json() as EmbeddingModelsConfigResponse;

    return {
      models: result.models,
      vectorSizeConstraints: result.vector_size_constraints,
    };
  }
}
