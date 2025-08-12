import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { NewConversation } from "@/components/conversation-view/new-conversation.tsx";
import {useApplicationContext} from "@/lib/use-application-context.ts";

export function NewChat() {
  const { availableAgents } = useApplicationContext()!;
  const { agent } = useParams();

  const agentId = agent ? parseInt(agent, 10) : null;
  const selectedAgent = availableAgents.find(agentObj => agentObj.id === agentId && !agentObj.corrupted);

  if (!selectedAgent) {
    return (
      <PageMain className="h-full">
        <PageHeading title="Choose Agent" description="Select an agent to start a conversation." className="sticky top-4 bg-white" />
        <div className="flex flex-col h-full px-4 pt-4">
          <div className="grow flex items-center justify-center">
            <div className="text-center space-y-4">
              <h2 className="text-xl font-semibold text-gray-900">No Agent Selected</h2>
              <p className="text-gray-600 max-w-md">
                Please choose an agent from the sidebar to start a new conversation.
              </p>
            </div>
          </div>
          <div className="bottom-0 sticky flex-shrink-0 bg-white pb-4">
          </div>
        </div>
      </PageMain>
    );
  }

  return (
    <PageMain className="h-full">
      <PageHeading title={selectedAgent.name} description="Start a new conversation." className="sticky top-4 bg-white" />
      <NewConversation agentId={selectedAgent.id} />
    </PageMain>
  );
}
