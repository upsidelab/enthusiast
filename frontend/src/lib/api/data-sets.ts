import { BaseApiClient } from "@/lib/api/base.ts";
import { DataSet, CatalogSource, User } from "@/lib/types.ts";

export type DataSetResponse = {
  id: number | undefined;
  name: string;
  language_model_provider: string;
  language_model: string;
  embedding_provider: string;
  embedding_model: string;
  embedding_vector_dimensions: number;
}

export type CreateDataSetPayload = DataSetResponse;

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

export class DataSetsApiClient extends BaseApiClient {
  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return (await response.json()).results as DataSet[];
  }

  async createDataSet(dataSet: DataSet): Promise<number> {
    const body: CreateDataSetPayload = {
      id: undefined,
      name: dataSet.name,
      language_model_provider: dataSet.languageModelProvider,
      language_model: dataSet.languageModel,
      embedding_provider: dataSet.embeddingProvider,
      embedding_model: dataSet.embeddingModel,
      embedding_vector_dimensions: dataSet.embeddingVectorSize,
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
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({plugin_name: pluginName, config: config})
      }
    );
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
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/document_sources`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({plugin_name: pluginName, config: config})
      }
    );
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
}
