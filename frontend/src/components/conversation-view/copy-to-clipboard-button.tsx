import { useState } from 'react';
import { Button } from '@/components/ui/button.tsx';
import { CopyIcon } from 'lucide-react';

export interface CopyToClipboardButtonProps {
  message: string;
}

export function CopyToClipboardButton({message}: CopyToClipboardButtonProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyClick = async () => {
    await navigator.clipboard.writeText(message);
    setIsCopied(true);

    setTimeout(() => {
      setIsCopied(false);
    }, 2000);
  };

  return (
    <Button onClick={handleCopyClick} variant="ghost">
      <CopyIcon />
      {isCopied ? 'Copied!' : 'Copy'}
    </Button>
  );
}
