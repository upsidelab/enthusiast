import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button.tsx";
import { Label } from "@/components/ui/label.tsx";
import { Textarea } from "@/components/ui/textarea.tsx"
import { HTMLAttributes, SyntheticEvent, useState } from "react";
import { Spinner } from "@/components/util/spinner.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { ApiClient } from "@/lib/api.ts";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert.tsx";
import { MessageFeedbackRating } from "@/components/message-feedback/message-feedback-rating.tsx";

interface MessageFeedbackFormProps {
  messageId: number | null;
}

const api = new ApiClient(authenticationProviderInstance);

export function MessageFeedbackForm({ messageId }: MessageFeedbackFormProps, { className, ...props }: HTMLAttributes<HTMLDivElement>) {
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [rating, setRating] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<string>("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  async function onSubmit(event: SyntheticEvent) {
    event.preventDefault();
    setIsLoading(true);

    const feedbackData = {
      rating: rating,
      feedback: feedback,
    };

    try {
      await api.conversations().updateMessageFeedback(messageId, feedbackData);
      setIsSubmitted(true);
    } catch {
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={onSubmit}>
        <div className="grid gap-4">
          <div className="grid gap-1">
            {isError && (
              <Alert variant="destructive">
                <AlertTitle>There was an error submitting your feedback.</AlertTitle>
                <AlertDescription>Please contact user support.</AlertDescription>
              </Alert>
            )}

            <Label className="sr-only" htmlFor="rating">Rating</Label>
            <MessageFeedbackRating disabled={isSubmitted} rating={rating} onRatingChange={setRating} />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="feedback">Your Feedback</Label>
            <Textarea
              disabled={isSubmitted}
              onChange={(event) => setFeedback(event.target.value)}
              className="bg-white"
              placeholder="Type your feedback here."
            />
          </div>

          <Button disabled={isLoading || isSubmitted} type="submit">
            { isSubmitted ?
              <>Thank you for your feedback!</>
              :
              <>
                {isLoading && <Spinner />}
                Submit Feedback
              </>
            }
          </Button>
        </div>
      </form>
    </div>
  );
}
