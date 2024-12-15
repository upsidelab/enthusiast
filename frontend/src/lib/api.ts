import { AuthenticationProvider } from "./authentication-provider.ts";

export type DataSet = {
  id: number | undefined;
  name: string;
  embeddingProvider: string;
  embeddingModel: string;
  embeddingVectorSize: number;
}

export type DataSetResponse = {
  id: number | undefined;
  name: string;
  embedding_provider: string;
  embedding_model: string;
  embedding_vector_dimensions: number;
}

export type CreateDataSetBody = DataSetResponse;

export type Product = {
  id: number;
  name: string;
  sku: string;
  slug: string;
  description: string;
  categories: string;
}

export type Document = {
  id: number;
  url: string;
  title: string;
  content: string;
}

export type Conversation = {
  id: number;
  started_at: Date;
  model: string;
  dimensions: number;
  data_set: string;
  history?: Message[];
}

export type Token = {
  token: string;
}

type AccountResponse = {
  email: string;
  is_staff: boolean;
}

export type Account = {
  email: string;
  isStaff: boolean;
}

export type User = {
  id: number;
  email: string;
}

export type FeedbackData = {
  rating: number | null;
  feedback: string;
}

export type Message = {
  id: number;
  role: string;
  text: string;
}

export interface PaginatedResult<T> {
  results: T[];
  count: number;
}

type CreateConversationRequestBody = {
  data_set_id: number;
}

type SendMessageBody = {
  question_message: string;
  conversation_id: number | null;
  data_set_id: number;
}

type TaskState = {
  state: string;
}

export type TaskHandle = {
  task_id: string;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider: AuthenticationProvider) {
    this.apiBase = import.meta.env.VITE_API_BASE;
  }

  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets/`, this._requestConfiguration());
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

    const response = await fetch(`${this.apiBase}/api/data_sets/`,
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

  async getProducts(dataSetId: number, page: number = 1): Promise<PaginatedResult<Product>> {
    const response = await fetch(`${this.apiBase}/api/products/${dataSetId}/?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Product>>;
  }

  async getDocuments(dataSetId: number, page: number = 1): Promise<PaginatedResult<Document>> {
    const response = await fetch(`${this.apiBase}/api/documents/${dataSetId}/?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Document>>;
  }

  async getConversations(dataSetId: number, page: number = 1): Promise<PaginatedResult<Conversation>> {
    const response = await fetch(`${this.apiBase}/api/conversations/${dataSetId}/?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Conversation>>;
  }

  async createConversation(dataSetId: number): Promise<number> {
    const requestBody: CreateConversationRequestBody = {
      data_set_id: dataSetId
    };

    const requestConfiguration = this._requestConfiguration();
    requestConfiguration.method = "POST";
    requestConfiguration.body = JSON.stringify(requestBody);

    const response = await fetch(`${this.apiBase}/api/conversation/`, requestConfiguration);

    if (!response.ok) {
      throw new Error(`Failed to create conversation: ${response.statusText}`);
    }

    const { id } = await response.json();
    return id;
  }

  async sendMessage(conversationId: number, dataSetId: number, message: string): Promise<TaskHandle> {
    const requestBody: SendMessageBody = {
      "question_message": message,
      "conversation_id": conversationId,
      "data_set_id": dataSetId
    }

    const response = await fetch(`${this.apiBase}/api/conversation/${conversationId}`, {
      ...this._requestConfiguration(),
      method: "POST",
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`Failed to enqueue task: ${response.statusText}`);
    }

    return await response.json() as TaskHandle;
  }

  async getTaskStatus(taskHandle: TaskHandle): Promise<string> {
    const response = await fetch(`${this.apiBase}/api/task_status/${taskHandle.task_id}`, {...this._requestConfiguration()});
    const { state } = await response.json() as TaskState;
    return state;
  }

  async fetchResponseMessage(conversationId: number, taskHandle: TaskHandle): Promise<Message | null> {
    const taskStatus = await this.getTaskStatus(taskHandle);

    if (taskStatus === "FAILURE") {
      throw new Error("Failed to get a response");
    }

    if (taskStatus === "SUCCESS") {
      const conversation = await this.getConversation(conversationId);
      return conversation.history![conversation.history!.length - 1];
    }

    return null;
  }

  async getConversation(conversation_id: number | null): Promise<Conversation> {
    try {
      const response = await fetch(`${this.apiBase}/api/conversation/${conversation_id}`, {
        ...this._requestConfiguration()
      });

      if (!response.ok) {
        throw new Error(`Failed to get conversation: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get conversation history: ${error.message}`);
      } else {
        throw new Error("Failed to get conversation history: An unknown error occurred.");
      }
    }
  }

  async login(email: string, password: string): Promise<Token> {
    const response = await fetch(`${this.apiBase}/api/auth/login`, {
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    if (response.status !== 200) {
      throw 'Could not sign in';
    }

    return await response.json() as Promise<Token>;
  }

  async getAccount(): Promise<Account> {
    const response = await fetch(`${this.apiBase}/api/account`, this._requestConfiguration());
    const responseJson = await response.json() as AccountResponse;
    return {
      email: responseJson.email,
      isStaff: responseJson.is_staff
    };
  }

  async getUsers(): Promise<User[]> {
    const response = await fetch(`${this.apiBase}/api/users`, this._requestConfiguration());
    return (await response.json()).results as User[];
  }

  async updateMessageFeedback(questionId: number | null, feedbackData: FeedbackData): Promise<void> {
    const response = await fetch(`${this.apiBase}/api/question/${questionId}/feedback/`, {
      ...this._requestConfiguration(),
      method: 'PATCH',
      body: JSON.stringify(feedbackData),
    });

    if (!response.ok) {
      throw new Error(`Could not update feedback for question ID ${questionId}`);
    }

    return await response.json() as Promise<void>;
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
