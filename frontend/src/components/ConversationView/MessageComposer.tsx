import { Button } from "@/components/ui/button.tsx";
import { Loader, Send } from "lucide-react";
import { ChangeEvent, useEffect, useRef, useState } from "react";
import './MessageComposer.css';
import { Textarea } from "@/components/ui/textarea.tsx";

export interface MessageComposerProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

const maxHeight = 300;

export function MessageComposer({ onSubmit, isLoading }: MessageComposerProps) {
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const inputLength = input.trim().length;

  const resizeTextArea = (element: HTMLTextAreaElement) => {
    element.style.height = '0px';
    element.style.height = `${Math.min(element.scrollHeight, maxHeight)}px`;
  }

  const handleTextAreaInput = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
    resizeTextArea(event.target);
  }

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
        <Textarea
          id="message"
          ref={inputRef}
          placeholder="Type your message..."
          className="w-full resize-none"
          autoComplete="off"
          value={input}
          onChange={(event) => handleTextAreaInput(event)}
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
