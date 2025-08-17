import { ConversationsList } from "@/components/conversations/conversations-list.tsx";
import { PageMain } from "@/components/util/page-main.tsx";
import { PageHeading } from "@/components/util/page-heading.tsx";

export function ChatHistory() {
  return (
    <PageMain>
      <PageHeading title="History" description="View your past conversations." />
      <ConversationsList />
    </PageMain>
  );
}
