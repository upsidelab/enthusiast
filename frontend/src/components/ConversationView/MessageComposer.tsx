import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Send } from "lucide-react";
import { useState } from "react";

export interface MessageComposerProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

export function MessageComposer({onSubmit}: MessageComposerProps) {
  const [input, setInput] = useState("");
  const inputLength = input.trim().length;

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        if (inputLength === 0) return;
        onSubmit(input);
        setInput("");
      }}
      className="flex w-full items-center space-x-2"
    >
      <Input
        id="message"
        placeholder="Type your message..."
        className="flex-1"
        autoComplete="off"
        value={input}
        onChange={(event) => setInput(event.target.value)}
      />
      <Button type="submit" size="icon" disabled={inputLength === 0}>
        <Send className="h-4 w-4"/>
        <span className="sr-only">Send</span>
      </Button>
    </form>
  );
}
