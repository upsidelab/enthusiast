import { BaseApiClient } from "@/lib/api/base.ts";
import { DataSet, CatalogSource, User } from "@/lib/types.ts";
import { ApiError } from "@/lib/api-error";

export type DataSetResponse = {
  id: number | undefined;
  name: string;
  language_model_provider: string;
  language_model: string;
  embedding_provider: string;
  embedding_model: string;
  embedding_vector_dimensions: number;
}

export type CreateDataSetPayload = DataSetResponse & {
  preconfigure_agents: boolean;
};

export type UpdateDataSetPayload = {
  id: number | undefined;
  name: string;
  language_model_provider: string;
  language_model: string;
}

export type ProductSourceResponse = {
  id: number;
  plugin_name: string;
  config: string;
  data_set_id: number;
}

export type ConfigureProductSourcePayload = ProductSourceResponse;

export type DocumentSourceResponse = {
  id: number;
  plugin_name: string;
  config: string;
  data_set_id: number;
}

export type ConfigureDocumentSourcePayload = DocumentSourceResponse;

export type ECommerceIntegrationResponse = {
  id: number;
  plugin_name: string;
  config: string;
  data_set_id: number;
}

export class DataSetsApiClient extends BaseApiClient {
  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return (await response.json()).results as DataSet[];
  }

  async createDataSet(dataSet: DataSet, preconfigureAgents: boolean): Promise<number> {
    const body: CreateDataSetPayload = {
      id: undefined,
      name: dataSet.name,
      language_model_provider: dataSet.languageModelProvider,
      language_model: dataSet.languageModel,
      embedding_provider: dataSet.embeddingProvider,
      embedding_model: dataSet.embeddingModel,
      embedding_vector_dimensions: dataSet.embeddingVectorSize,
      preconfigure_agents: preconfigureAgents,
    }

    const response = await fetch(`${this.apiBase}/api/data_sets`,
      {
        ...this._requestConfiguration(),
        body: JSON.stringify(body),
        method: 'POST'
      }
    );

    const responseJson = (await response.json()) as DataSetResponse;
    return responseJson.id!;
  }

  async getDataSetUsers(dataSetId: number): Promise<User[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/users`, this._requestConfiguration());
    return (await response.json()).results as User[];
  }

  async addDataSetUser(dataSetId: number, userId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/users`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({user_id: userId})
      }
    );
  }

  async removeDataSetUser(dataSetId: number, userId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/users/${userId}`,
      {
        ...this._requestConfiguration(),
        method: "DELETE"
      }
    );
  }

  async configureDataSetProductSource(productSource: CatalogSource): Promise<number> {
    const body: ConfigureProductSourcePayload = {
      id: productSource.id,
      plugin_name: productSource.plugin_name,
      config: JSON.parse(productSource.config),
      data_set_id: productSource.data_set_id
    }

    const response = await fetch(`${this.apiBase}/api/data_sets/${productSource.data_set_id}/product_sources/${productSource.id}`,
      {
        ...this._requestConfiguration(),
        body: JSON.stringify(body),
        method: 'PATCH'
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(`Failed to configure product source: ${response.statusText}`, {
        data: errorData,
        status: response.status
      });
    }

    const responseJson = (await response.json()) as ProductSourceResponse;
    return responseJson.id!;
  }

  async getDataSetProductSource(dataSetId: number, productSourceId: number): Promise<CatalogSource> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/product_sources/${productSourceId}`, this._requestConfiguration());
    return await response.json() as CatalogSource;
  }

  async getDataSetProductSources(dataSetId: number): Promise<CatalogSource[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/product_sources`, this._requestConfiguration());
    return (await response.json()).results as CatalogSource[];
  }

  async addDataSetProductSource(dataSetId: number, pluginName: string, config: object): Promise<void> {
    const response = await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({plugin_name: pluginName, config: config})
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(`Failed to add product source: ${response.statusText}`, {
        data: errorData,
        status: response.status
      });
    }
  }

  async syncAllProductSources(): Promise<void> {
    await fetch(
      `${this.apiBase}/api/product_sources/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async syncDataSetProductSources(dataSetId: number | undefined): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async syncDataSetProductSource(dataSetId: number, pluginId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources/${pluginId}/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async removeDataSetProductSource(dataSetId: number, pluginId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources/${pluginId}`,
      {
        ...this._requestConfiguration(),
        method: "DELETE"
      }
    );
  }

  async configureDataSetDocumentSource(documentSource: CatalogSource): Promise<number> {
    const body: ConfigureDocumentSourcePayload = {
      id: documentSource.id,
      plugin_name: documentSource.plugin_name,
      config: JSON.parse(documentSource.config),
      data_set_id: documentSource.data_set_id
    }

    const response = await fetch(`${this.apiBase}/api/data_sets/${documentSource.data_set_id}/document_sources/${documentSource.id}`,
      {
        ...this._requestConfiguration(),
        body: JSON.stringify(body),
        method: 'PATCH'
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(`Failed to configure document source: ${response.statusText}`, {
        data: errorData,
        status: response.status
      });
    }

    const responseJson = (await response.json()) as DocumentSourceResponse;
    return responseJson.id!;
  }

  async getDataSetDocumentSource(dataSetId: number, documentSourceId: number): Promise<CatalogSource> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/document_sources/${documentSourceId}`, this._requestConfiguration());
    return await response.json() as CatalogSource;
  }

  async getDataSetDocumentSources(dataSetId: number): Promise<CatalogSource[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/document_sources`, this._requestConfiguration());
    return (await response.json()).results as CatalogSource[];
  }

  async addDataSetDocumentSource(dataSetId: number, pluginName: string, config: object): Promise<void> {
    const response = await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/document_sources`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({plugin_name: pluginName, config: config})
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(`Failed to add document source: ${response.statusText}`, {
        data: errorData,
        status: response.status
      });
    }
  }

  async syncAllDocumentSources(): Promise<void> {
    await fetch(
      `${this.apiBase}/api/document_sources/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async syncDataSetDocumentSources(dataSetId: number | undefined): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/document_sources/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async syncDataSetDocumentSource(dataSetId: number, pluginId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/document_sources/${pluginId}/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async removeDataSetDocumentSource(dataSetId: number, pluginId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/document_sources/${pluginId}`,
      {
        ...this._requestConfiguration(),
        method: "DELETE"
      }
    );
  }

  async syncDataSetAllSources(dataSetId: number | undefined): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async syncAllSources(): Promise<void> {
    await fetch(
      `${this.apiBase}/api/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async getDataSet(dataSetId: number): Promise<DataSet> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}`, this._requestConfiguration());
    const data = await response.json();
    
    return {
      id: data.id,
      name: data.name,
      languageModelProvider: data.language_model_provider,
      languageModel: data.language_model,
      embeddingProvider: data.embedding_provider,
      embeddingModel: data.embedding_model,
      embeddingVectorSize: data.embedding_vector_dimensions,
    } as DataSet;
  }

  async updateDataSet(dataSetId: number, dataSet: DataSet): Promise<void> {
    const body: UpdateDataSetPayload = {
      id: dataSet.id,
      name: dataSet.name,
      language_model_provider: dataSet.languageModelProvider,
      language_model: dataSet.languageModel,
    }

    await fetch(`${this.apiBase}/api/data_sets/${dataSetId}`,
      {
        ...this._requestConfiguration(),
        method: 'PATCH',
        body: JSON.stringify(body)
      }
    );
  }

  async getDataSetECommerceIntegration(dataSetId: number): Promise<ECommerceIntegrationResponse | null> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/ecommerce_integration`, this._requestConfiguration());
    
    if (response.status === 404) {
      return null;
    }
    
    return await response.json() as ECommerceIntegrationResponse;
  }

  async addDataSetECommerceIntegration(dataSetId: number, pluginName: string, config: object): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/ecommerce_integration`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({ plugin_name: pluginName, config: config })
      }
    );
  }

  async configureDataSetECommerceIntegration(updated_source: CatalogSource): Promise<void> {
    const body = {
      id: updated_source.id,
      plugin_name: updated_source.plugin_name,
      config: JSON.parse(updated_source.config),
      data_set_id: updated_source.data_set_id
    };

    await fetch(`${this.apiBase}/api/data_sets/${updated_source.data_set_id}/ecommerce_integration`,
      {
        ...this._requestConfiguration(),
        body: JSON.stringify(body),
        method: 'PATCH'
      }
    );
  }

  async syncDataSetEcommerceIntegration(dataSetId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/ecommerce_integration/sync`,
      {
        ...this._requestConfiguration(),
        method: "POST"
      }
    );
  }

  async removeDataSetECommerceIntegration(dataSetId: number): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/ecommerce_integration`,
      {
        ...this._requestConfiguration(),
        method: "DELETE"
      }
    );
  }
}
