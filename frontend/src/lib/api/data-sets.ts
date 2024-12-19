import { BaseApiClient } from "@/lib/api/base.ts";
import { DataSet, ProductSource, User } from "@/lib/types.ts";

export type DataSetResponse = {
  id: number | undefined;
  name: string;
  embedding_provider: string;
  embedding_model: string;
  embedding_vector_dimensions: number;
}

export type CreateDataSetPayload = DataSetResponse;

export type ProductSourceResponse = {
  id: number;
  plugin_name: string;
  config: string;
  data_set_id: number;
}

export type ConfigureProductSourcePayload = ProductSourceResponse;

export class DataSetsApiClient extends BaseApiClient {
  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return (await response.json()).results as DataSet[];
  }

  async createDataSet(dataSet: DataSet): Promise<number> {
    const body: CreateDataSetPayload = {
      id: undefined,
      name: dataSet.name,
      embedding_provider: dataSet.embeddingProvider,
      embedding_model: dataSet.embeddingModel,
      embedding_vector_dimensions: dataSet.embeddingVectorSize
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

  async configureDataSetProductSource(productSource: ProductSource): Promise<number> {
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

  async getDataSetProductSource(dataSetId: number, productSourceId: number): Promise<ProductSource> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/product_sources/${productSourceId}`, this._requestConfiguration());
    return await response.json() as ProductSource;
  }

  async getDataSetProductSources(dataSetId: number): Promise<ProductSource[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets/${dataSetId}/product_sources`, this._requestConfiguration());
    return (await response.json()).results as ProductSource[];
  }

  async addDataSetProductSource(dataSetId: number, pluginName: string): Promise<void> {
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify({plugin_name: pluginName})
      }
    );
  }

  async removeDataSetProductSource(dataSetId: number, pluginId: number): Promise<void> {
    console.log("dataSetId:", dataSetId, "pluginId: ", pluginId);
    await fetch(
      `${this.apiBase}/api/data_sets/${dataSetId}/product_sources/${pluginId}`,
      {
        ...this._requestConfiguration(),
        method: "DELETE"
      }
    );
  }

}
