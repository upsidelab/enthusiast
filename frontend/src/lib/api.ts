import { AuthenticationProvider } from "./authentication-provider.ts";

export type DataSet = {
  id: number;
  code: string;
  name: string;
}

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
  started_at: Date;
  model: string;
  dimensions: number;
  data_set: string;
}

export type Token = {
  token: string;
}

export type Answer = {
  conversation_id: number;
  query_message: string;
  answer: string;
}

export type Account = {
  email: string;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider: AuthenticationProvider) {
    this.apiBase = import.meta.env.VITE_API_BASE;
  }

  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return await response.json() as Promise<DataSet[]>;
  }

  async getProducts(dataSetId: number): Promise<Product[]> {
    const response = await fetch(`${this.apiBase}/api/products/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Product[]>;
  }

  async getDocuments(dataSetId: number): Promise<Document[]> {
    const response = await fetch(`${this.apiBase}/api/documents/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Document[]>;
  }

  async getConversations(dataSetId: number): Promise<Conversation[]> {
    const response = await fetch(`${this.apiBase}/api/conversations/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Conversation[]>;
  }

  async getAnswer(conversation_id: number | null, message: string) {
    try {
      type RequestBody = {
         question_message: string;
         conversation_id?: number;
       };

      const body: RequestBody = { "question_message": message }
      if (conversation_id !== null) {
        body.conversation_id = conversation_id
      }

      // Step 1: Enqueue the task
      const response = await fetch(`${this.apiBase}/api/ask/`, {
        headers: {
          ...this._requestConfiguration().headers,
          'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        throw new Error(`Failed to enqueue task: ${response.statusText}`);
      }

      const data = await response.json();
      const taskId = data.task_id;

      // Step 2: Polling function to check task status (with a defined frequency)
      const pollTaskStatus = async (taskId: string): Promise<any> => {
        return new Promise((resolve, reject) => {
          const pollInterval = setInterval(async () => {
            try {
              const response = await fetch(`${this.apiBase}/api/task_status/${taskId}/`, {
                headers: {
                  ...this._requestConfiguration().headers,
                  'Content-Type': 'application/json'
                },
                method: 'GET'
              });

              if (!response.ok) {
                throw new Error(`Failed to fetch task status: ${response.statusText}`);
              }

              const data = await response.json();
              const { state, result } = data;

              if (state === "SUCCESS") {
                clearInterval(pollInterval);
                resolve(result);
              } else if (state === "FAILURE") {
                clearInterval(pollInterval);
                reject(new Error("Task failed"));
              }
            } catch (error) {
              clearInterval(pollInterval);
              reject(error);
            }
          }, 2000); // Polling interval.
        });
      };

      // Step 3: Await polling result and return final answer
      return await pollTaskStatus(taskId);
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get answer: ${error.message}`);
      } else {
        throw new Error("Failed to get answer: An unknown error occurred.");
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
    return await response.json() as Promise<Account>;
  }

  _requestConfiguration(): RequestInit {
    return {
      headers: {
        'Authorization': `Token ${this.authenticationProvider.token}`
      }
    }
  }
}
