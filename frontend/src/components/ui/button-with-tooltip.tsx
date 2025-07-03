import { Button } from "@/components/ui/button.tsx";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip.tsx";
import { ButtonProps } from "@/components/ui/button.tsx";
import { ReactNode } from "react";

export interface ButtonWithTooltipProps extends ButtonProps {
  tooltip: string;
  children: ReactNode;
}

export function ButtonWithTooltip({ tooltip, children, ...buttonProps }: ButtonWithTooltipProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button {...buttonProps}>
          {children}
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>{tooltip}</p>
      </TooltipContent>
    </Tooltip>
  );
} 