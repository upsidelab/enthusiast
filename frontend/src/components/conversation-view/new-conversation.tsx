import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { MessageComposer } from "@/components/conversation-view/message-composer.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useState, useEffect } from "react";
import { AgentDetails } from "@/lib/types";

const api = new ApiClient(authenticationProviderInstance);

export interface NewConversationProps {
  agentId: number;
}

export function NewConversation({ agentId }: NewConversationProps) {
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();
  const [agent, setAgent] = useState<AgentDetails>();

  useEffect(() => {
    const loadAgentDetails = async () => {
      try {
        const agentDetails = await api.agents().getAgentById(agentId);
        setAgent(agentDetails);
      } catch (error) {
        console.error('Failed to load agent details:', error);
      }
    };

    loadAgentDetails();
  }, [agentId]);

  const onSubmit = async (message: string, _fileIds?: number[], createdConversationId?: number) => {
    if (createdConversationId) {
      navigate(`/data-sets/${dataSetId}/chat/${createdConversationId}?pending=${message}`);
    } else {
      const newConversationId = await api.conversations().createConversation(agentId);
      navigate(`/data-sets/${dataSetId}/chat/${newConversationId}?pending=${message}`);
    }
  }

  return (
    <div className="flex flex-col h-full px-4 pt-4">
      <div className="grow flex items-start justify-center pt-16">
        {agent?.description && (
          <div className="text-center space-y-4 max-w-2xl px-6">
            <div className="bg-background rounded-lg p-6">
              <p className="text-gray-500 text-base leading-relaxed">
                {agent.description}
              </p>
            </div>
          </div>
        )}
      </div>
      <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
        <MessageComposer onSubmit={onSubmit} isLoading={false} agentId={agentId}/>
      </div>
    </div>
  )
}
