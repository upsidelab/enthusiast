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

export type Account = {
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

interface PaginatedResult<T> {
  results: T[];
  count: number;
}

export class ApiClient {
  private readonly apiBase: string;

  constructor(private readonly authenticationProvider: AuthenticationProvider) {
    this.apiBase = import.meta.env.VITE_API_BASE;
  }

  async getDataSets(): Promise<DataSet[]> {
    const response = await fetch(`${this.apiBase}/api/data_sets`, this._requestConfiguration());
    return (await response.json()).results as DataSet[];
  }

  async getProducts(dataSetId: number, page: number = 1): Promise<PaginatedResult<Product>> {
    const response = await fetch(`${this.apiBase}/api/products/${dataSetId}/?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Product>>;
  }

  async getDocuments(dataSetId: number, page: number = 1): Promise<PaginatedResult<Document>> {
    const response = await fetch(`${this.apiBase}/api/documents/${dataSetId}/?page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Document>>;
  }

  async getConversations(dataSetId: number): Promise<Conversation[]> {
    const response = await fetch(`${this.apiBase}/api/conversations/${dataSetId}`, this._requestConfiguration());
    return await response.json() as Promise<Conversation[]>;
  }

  async getAnswer(conversation_id: number | null, dataSetId: number, message: string) {
    try {
      type RequestBody = {
         question_message: string;
         conversation_id: number | null;
         data_set_id: number;
       };

      // Initialize a conversation
      if (conversation_id === null) {
        try {
          const response = await fetch(`${this.apiBase}/api/conversation/`, {
            method: "POST",
            headers: {
              ...this._requestConfiguration().headers,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({"data_set_id": dataSetId})
          });

          if (!response.ok) {
            throw new Error(`Failed to create conversation: ${response.statusText}`);
          }

          const data = await response.json();
          conversation_id = data.id;
        } catch (error) {
          console.error("Error creating conversation:", error);
          throw error;
        }
      }

      const body: RequestBody = {
        "question_message": message,
        "conversation_id": conversation_id,
        "data_set_id": dataSetId
      }

      // Enqueue the task
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

      // Polling function to check task status (with a defined interval)
      const pollTaskStatus = async (taskId: string): Promise<string> => {
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
              const { state } = data;

              if (state === "SUCCESS") {
                clearInterval(pollInterval);
                resolve(state);
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
      // Function to wait for task and return history.
      const status = await pollTaskStatus(taskId);

      if (status === "SUCCESS") {
        const conversation = await this.getConversation(conversation_id);
        const latestMessage = conversation.history?.[conversation.history.length - 1];  //Latest message is an answer.
        return {
            conversation_id: conversation_id,
            answer: latestMessage?.text || "No answer available",
            message_id: latestMessage?.id || null,
        };
      }
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get answer: ${error.message}`);
      } else {
        throw new Error("Failed to get answer: An unknown error occurred.");
      }
    }
  }

  async getConversation(conversation_id: number | null): Promise<Conversation> {
    try {
      const response = await fetch(`${this.apiBase}/api/conversation/${conversation_id}`, {
        headers: {
          ...this._requestConfiguration().headers,
          'Content-Type': 'application/json'
        },
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Failed to get conversation: ${response.statusText}`);
      }

      const conversation = await response.json();

      return conversation;
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
    return await response.json() as Promise<Account>;
  }

  async updateMessageFeedback(questionId: number | null, feedbackData: FeedbackData): Promise<void> {
    const response = await fetch(`${this.apiBase}/api/question/${questionId}/feedback/`, {
      headers: {
        ...this._requestConfiguration().headers,
        'Content-Type': 'application/json',
      },
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
        'Authorization': `Token ${this.authenticationProvider.token}`
      }
    }
  }
}
