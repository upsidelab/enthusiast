import { Button } from '@/components/ui/button.tsx';
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react';

export interface FeedbackButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export function FeedbackButton({isOpen, onClick}: FeedbackButtonProps) {
  return (
    <Button onClick={onClick} variant="ghost">
      Provide feedback for this response
      {isOpen ? <ChevronUpIcon/> : <ChevronDownIcon/>}
    </Button>
  );
}