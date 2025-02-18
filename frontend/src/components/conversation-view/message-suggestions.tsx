import { Button } from "@/components/ui/button.tsx";
import { cn } from "@/lib/utils.ts";

export interface MessageSuggestionsProps {
  onClick: (message: string) => void;
  hidden: boolean;
}

export function MessageSuggestions({ onClick, hidden }: MessageSuggestionsProps) {
  const additionalStyles = hidden ? 'opacity-0 translate-y-4' : '';

  const suggestedMessages = [
    'Which plans include an SLA?',
    'List all channels available in FiberUp 1GB Premium',
    'What\'s the roaming cost for Switzerland in MobileUp 5GB?'
  ];

  return (
    <div className={cn("flex space-x-4 items-center mb-4 transition ease-out", additionalStyles)}>
      <p className="text-sm">Try asking:</p>
      {
        suggestedMessages.map((message) => (
          <Button onClick={() => onClick(message)} variant="secondary">{message}</Button>
        ))
      }
    </div>
  )
}
