import { CheckCircle2, CircleFadingArrowUp } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip.tsx";

export interface IndexingStatusIconProps {
  isIndexed: boolean;
}

export function IndexingStatusIcon({ isIndexed }: IndexingStatusIconProps) {
  const label = isIndexed ? "Indexed" : "Waiting for indexing...";
  const icon = isIndexed ? <CheckCircle2 size={16}/> : <CircleFadingArrowUp size={16}/>;
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>{icon}</TooltipTrigger>
        <TooltipContent>
          <p>{label}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
