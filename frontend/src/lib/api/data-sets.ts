import { AuthenticationProvider } from "@/lib/authentication-provider.ts";
import { CreateDataSetBody, DataSet, DataSetResponse, User } from "@/lib/api.ts";

export class DataSetsApiClient {
  constructor(private readonly apiBase: string, private readonly authenticationProvider: AuthenticationProvider) {}

  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return (await response.json()).results as DataSet[];
  }

  async createDataSet(dataSet: DataSet): Promise<number> {
    const body: CreateDataSetBody = {
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

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Token ${this.authenticationProvider.token}`,
        "Content-Type": "application/json"
      }
    }
  }
}
