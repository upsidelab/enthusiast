import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Send, Loader } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import './MessageComposer.css';

export interface MessageComposerProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

export function MessageComposer({ onSubmit, isLoading }: MessageComposerProps) {
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const inputLength = input.trim().length;

  // Focus back to the input field after response is received.
  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        if (inputLength === 0) return;
        onSubmit(input);
        setInput("");
      }}
      className="flex w-full items-center space-x-2 relative"
    >
      <div className="relative flex-1">
        <Input
          id="message"
          ref={inputRef}
          placeholder="Type your message..."
          className="w-full"
          autoComplete="off"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={isLoading}
        />
      </div>
      <Button type="submit" size="icon" disabled={isLoading || inputLength === 0}>
        {isLoading ? (
          <Loader className="h-4 w-4 animate-spin text-gray-500" />
        ) : (
          <Send className="h-4 w-4" />
        )}
        <span className="sr-only">Send</span>
      </Button>
    </form>
  );
}
