import { useState } from "react";
import { Button } from "@/components/ui/button.tsx";
import { cn } from "@/lib/utils.ts";
import Logo from "@/assets/logo.svg";
import { MessageComposer } from "@/components/conversation-view/message-composer.tsx";
import { samplePrompts } from "@/constants/prompts.ts";

export function WelcomePanel({ onSendMessage }: { onSendMessage: (message: string) => void }) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (msg: string) => {
    setIsLoading(true);
    onSendMessage(msg);
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-6 space-y-6 bg-gray-50 rounded-lg shadow-lg">
      <img src={Logo} alt="Logo" className="w-24 h-24" />
      <h2 className="text-3xl font-bold text-gray-800">Welcome to Enthusiast</h2>
      <p className="text-lg text-gray-600">How can I help you today?</p>
      <div className="flex flex-wrap justify-center space-x-2">
        {samplePrompts.map((prompt, index) => (
          <Button
            key={index}
            onClick={() => handleSendMessage(prompt)}
            variant="outline"
            className="border-gray-300 bg-gray-50 text-gray-800 rounded-lg p-2"
          >
            {prompt}
          </Button>
        ))}
      </div>
      <div className="w-full mt-4">
        <MessageComposer onSubmit={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}