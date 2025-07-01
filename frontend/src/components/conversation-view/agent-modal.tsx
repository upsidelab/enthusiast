import {AgentSelectionForm} from "@/components/conversation-view/agent-modal-form.tsx";

export interface AgentModalProps {
  show: boolean;
  onClose: (selectedAgent: string) => void;
  currentAgent: string
}

export function AgentModal({ show, onClose, currentAgent }: AgentModalProps) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white p-4 rounded shadow-lg max-w-md w-full">
        <h2 className="text-lg font-bold mb-4">Choose an agent</h2>
        <AgentSelectionForm
          currentAgent={currentAgent}
          onSubmit={onClose}
        />
      </div>
    </div>
  );
}