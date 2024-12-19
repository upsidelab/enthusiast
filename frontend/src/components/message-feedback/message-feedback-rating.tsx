import { Button } from "@/components/ui/button.tsx";

interface MessageFeedbackRatingProps {
  rating: number | null;
  disabled: boolean;
  onRatingChange: (value: number) => void;
}

const values = [
  {value: 1, label: 'Poor'},
  {value: 2, label: 'Fair'},
  {value: 3, label: 'Good'},
  {value: 4, label: 'Very Good'},
  {value: 5, label: 'Excellent'},
];

export function MessageFeedbackRating({onRatingChange, rating, disabled}: MessageFeedbackRatingProps) {
  const classNamesForButton = (value: number) => {
    if (value === rating) {
      return "border border-black";
    }
    return "";
  };

  return (
    <div className="flex space-x-2">
      {values.map(({value, label}) => (
        <Button variant="outline"
                disabled={disabled}
                type="button"
                className={classNamesForButton(value)}
                onClick={() => onRatingChange(value)}>
          {label}
        </Button>
      ))}
    </div>
  );
}
