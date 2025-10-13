import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { NewConversation } from "@/components/conversation-view/new-conversation.tsx";
import {useApplicationContext} from "@/lib/use-application-context.ts";

import type { OnPendingMessage } from "@/components/conversation-view/chat";

interface EmptyStateProps {
  title: string;
  description: string;
  pageTitle: string;
  pageDescription: string;
}

interface NewChatProps {
  onPendingMessage: OnPendingMessage;
}

function EmptyState({ title, description, pageTitle, pageDescription }: EmptyStateProps) {
  return (
    <PageMain className="h-full">
      <PageHeading title={pageTitle} description={pageDescription} className="sticky top-4 bg-white" />
      <div className="flex flex-col h-full px-4 pt-4">
        <div className="grow flex items-center justify-center">
          <div className="text-center space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
            <p className="text-gray-600 max-w-md">
              {description}
            </p>
          </div>
        </div>
        <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
        </div>
      </div>
    </PageMain>
  );
}

export function NewChat({ onPendingMessage }: NewChatProps) {
  const { availableAgents } = useApplicationContext()!;
  const { agent } = useParams();

  if (availableAgents.length === 0) {
    return (
      <EmptyState
        title="No Agents Available"
        description="There are currently no agents available for this dataset."
        pageTitle="No Agents Available"
        pageDescription="There are currently no agents for this dataset."
      />
    );
  }

  const agentId = agent ? parseInt(agent, 10) : null;
  if (!agentId) {
    return (
      <EmptyState
        title="No Agent Selected"
        description="Please choose an agent from the sidebar to start a new conversation."
        pageTitle="Choose Agent"
        pageDescription="Select an agent to start a conversation."
      />
    );
  }

  const selectedAgent = availableAgents.find(agentObj => agentObj.id === agentId);

  if (!selectedAgent) {
    return (
      <EmptyState
        title="Agent Not Found"
        description="The selected agent could not be found or may have been removed."
        pageTitle="Agent Not Found"
        pageDescription="The requested agent is not available."
      />
    );
  }

  

  return (
    <PageMain className="h-full">
      <PageHeading title={selectedAgent.name} description="Start a new conversation." className="sticky top-4 bg-white" />
      <NewConversation agentId={selectedAgent.id} onPendingMessage={onPendingMessage} />
    </PageMain>
  );
}
