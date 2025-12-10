import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { ChatWindow } from "@/components/conversation-view/chat-window.tsx";

import type { AgentDetails } from "@/lib/types";
import type { OnPendingMessage } from "@/pages/data-sets/(id)/chat/index.tsx";
import type { OnSubmit } from "@/components/conversation-view/message-composer.tsx";

interface NewChatProps {
  onPendingMessage: OnPendingMessage;
}

const api = new ApiClient(authenticationProviderInstance);

export function NewChat({ onPendingMessage }: NewChatProps) {
  const { availableAgents, supportedFileExtensions } = useApplicationContext()!;
  const { agent } = useParams();
  const [agentDetails, setAgentDetails] = useState<AgentDetails>();

  const agentId = agent ? parseInt(agent, 10) : null;
  const selectedAgent = agentId ? availableAgents.find(agentObj => agentObj.id === agentId) : null;

  const emptyState = (() => {
    if (availableAgents.length === 0) {
      return {
        title: 'No Agents Available',
        description: 'There are currently no agents available for this dataset.',
        pageTitle: 'No Agents Available',
        pageDescription: 'There are currently no agents for this dataset.'
      };
    }

    if (!agentId) {
      return {
        title: 'No Agent Selected',
        description: 'Please choose an agent from the sidebar to start a new conversation.',
        pageTitle: 'Choose Agent',
        pageDescription: 'Select an agent to start a conversation.'
      };
    }
    
    if (!selectedAgent) {
      return {
        title: 'Agent Not Found',
        description: 'The selected agent could not be found or may have been removed.',
        pageTitle: 'Agent Not Found',
        pageDescription: 'The requested agent is not available.'
      };
    }

    return false;
  })();

  useEffect(() => {
    const loadAgentDetails = async () => {
      if (!selectedAgent) {
        return;
      }

      try {
        const agentDetails = await api.agents().getAgentById(selectedAgent.id);
        setAgentDetails(agentDetails);
      } catch (error) {
        console.error('Failed to load agent details:', error);
      }
    };

    loadAgentDetails();
  }, [selectedAgent]);

  const onSubmit: OnSubmit = async (message, createdConversationId) => {
    const conversationId = createdConversationId || await api.conversations().createConversation(selectedAgent!.id);
    onPendingMessage(message, conversationId);
  }

  return (
    <PageMain className="h-full">
      <PageHeading
        title={emptyState && emptyState.title || selectedAgent!.name}
        description={emptyState && emptyState.description || 'Start a new conversation.'}
        className="sticky top-4 bg-white z-10"
      />
      {
        emptyState ? (
          <div className="flex flex-col h-full px-4 pt-4">
            <div className="grow flex items-center justify-center">
              <div className="text-center space-y-4">
                <h2 className="text-xl font-semibold text-gray-900">{emptyState.title}</h2>
                <p className="text-gray-600 max-w-md">
                  {emptyState.description}
                </p>
              </div>
            </div>
            <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
            </div>
          </div>
        ) : (
          <ChatWindow className="pt-4" onSubmit={onSubmit} isLoading={false} agentId={agentId ?? undefined} fileUploadEnabled={agentDetails?.file_upload && supportedFileExtensions.length > 0}>
            <div className="grow flex items-start justify-center pt-16">
              {agentDetails?.description && (
                <div className="text-center space-y-4 max-w-2xl px-6">
                  <div className="bg-background rounded-lg p-6">
                    <p className="text-gray-500 text-base leading-relaxed">
                      {agentDetails.description}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </ChatWindow>
        )
      }
    </PageMain>
  );
}
