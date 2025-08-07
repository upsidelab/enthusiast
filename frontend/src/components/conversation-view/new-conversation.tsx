import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { MessageComposer } from "@/components/conversation-view/message-composer.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface NewConversationProps {
  agentId: string;
}

export function NewConversation({ agentId }: NewConversationProps) {
  const { dataSetId } = useApplicationContext()!;
  const navigate = useNavigate();

  const onSubmit = async (message: string) => {
    const newConversationId = await api.conversations().createConversation(agentId);

    navigate(`/data-sets/${dataSetId}/chat/${newConversationId}?pending=${message}`);
  }

  return (
    <div className="flex flex-col h-full px-4 pt-4">
      <div className="grow" />
      <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
        <MessageComposer onSubmit={onSubmit} isLoading={false}/>
      </div>
    </div>
  )
}
