import { FeedbackData, TaskHandle } from "@/lib/api.ts";
import { BaseApiClient } from "@/lib/api/base.ts";
import { Conversation, Message, PaginatedResult } from "@/lib/types.ts";

export type CreateConversationPayload = {
  data_set_id: number;
}

export type CreateMessagePayload = {
  question_message: string;
  conversation_id: number | null;
  data_set_id: number;
}

type TaskState = {
  state: string;
}


export class ConversationsApiClient extends BaseApiClient {
  async getConversations(dataSetId: number, page: number = 1): Promise<PaginatedResult<Conversation>> {
    const response = await fetch(`${this.apiBase}/api/conversations?data_set_id=${dataSetId}&page=${page}`, this._requestConfiguration());
    return await response.json() as Promise<PaginatedResult<Conversation>>;
  }

  async createConversation(dataSetId: number): Promise<number> {
    const requestBody: CreateConversationPayload = {
      data_set_id: dataSetId
    };

    const requestConfiguration = this._requestConfiguration();
    requestConfiguration.method = "POST";
    requestConfiguration.body = JSON.stringify(requestBody);

    const response = await fetch(`${this.apiBase}/api/conversations`, requestConfiguration);

    if (!response.ok) {
      throw new Error(`Failed to create conversation: ${response.statusText}`);
    }

    const { id } = await response.json();
    return id;
  }

  async sendMessage(conversationId: number, dataSetId: number, message: string): Promise<TaskHandle> {
    const requestBody: CreateMessagePayload = {
      "question_message": message,
      "conversation_id": conversationId,
      "data_set_id": dataSetId
    }

    const response = await fetch(`${this.apiBase}/api/conversations/${conversationId}`, {
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

    if (taskStatus === "SUCCESS" || taskStatus === "FAILURE") {
      const conversation = await this.getConversation(conversationId);
      return conversation.history![conversation.history!.length - 1];
    }

    return null;
  }

  async getConversation(conversation_id: number | null): Promise<Conversation> {
    try {
      const response = await fetch(`${this.apiBase}/api/conversations/${conversation_id}`, {
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

  async updateMessageFeedback(messageId: number | null, feedbackData: FeedbackData): Promise<void> {
    const response = await fetch(`${this.apiBase}/api/messages/${messageId}/feedback/`, {
      ...this._requestConfiguration(),
      method: 'PATCH',
      body: JSON.stringify(feedbackData),
    });

    if (!response.ok) {
      throw new Error(`Could not update feedback for message ID ${messageId}`);
    }

    return await response.json() as Promise<void>;
  }
}
