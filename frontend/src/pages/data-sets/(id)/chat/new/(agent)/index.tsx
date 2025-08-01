import { useParams } from "react-router-dom";
import { PageHeading } from "@/components/util/page-heading.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { NewConversation } from "@/components/conversation-view/new-conversation.tsx";
import {useApplicationContext} from "@/lib/use-application-context.ts";

export function NewChat() {
  const { availableAgents } = useApplicationContext()!;
  const { agent } = useParams();

  const selectedAgent = availableAgents.find(agentObj => agentObj.key === agent);
  const agentName = selectedAgent?.name ?? "Question Answer Agent";
  const agentKey = agent ? agent : "question_answer_agent"

  return (
    <PageMain className="h-full">
      <PageHeading title={agentName} description="Start a new conversation." className="sticky top-4 bg-white" />
      <NewConversation agent={agentKey} />
    </PageMain>
  );
}
