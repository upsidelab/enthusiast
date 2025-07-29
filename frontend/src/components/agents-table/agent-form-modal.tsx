import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Agent } from "@/lib/types";
import { useRef, useEffect, useState } from "react";
import { useAgentForm } from "./hooks/use-agent-form";
import { AgentConfigurationForm } from "./agent-configuration-form";

interface AgentFormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agent: Agent | null;
  agentTypes: any[];
  loadingTypes: boolean;
  dataSetId: number | null;
  onSuccess: () => void;
}

export function AgentFormModal({
  open,
  onOpenChange,
  agent,
  agentTypes,
  loadingTypes,
  dataSetId,
  onSuccess
}: AgentFormModalProps) {
  const {
    name,
    setName,
    type,
    setType,
    config,
    setConfig,
    agentConfigSections,
    openSections,
    setOpenSections,
    fieldErrors,
    generalError,
    submitting,
    handleSubmit
  } = useAgentForm(agent, agentTypes, dataSetId, onSuccess);

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showFade, setShowFade] = useState(false);

  const handleClose = () => {
    onOpenChange(false);
  };

  useEffect(() => {
    const checkIfScrollingNeeded = () => {
      if (scrollContainerRef.current) {
        const { scrollHeight, clientHeight } = scrollContainerRef.current;
        const hasOverflow = scrollHeight > clientHeight;
        setShowFade(hasOverflow);
      }
    };

    const setupScrollObserver = () => {
      const resizeObserver = new ResizeObserver(checkIfScrollingNeeded);
      if (scrollContainerRef.current) {
        resizeObserver.observe(scrollContainerRef.current);
      }
      return resizeObserver;
    };

    const cleanupScrollObserver = (observer: ResizeObserver) => {
      observer.disconnect();
    };

    checkIfScrollingNeeded();
    const observer = setupScrollObserver();
    return () => cleanupScrollObserver(observer);
  }, [type, agentConfigSections, openSections, generalError, fieldErrors]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>{agent ? `Edit Agent` : `New Agent`}</DialogTitle>
        </DialogHeader>
        
        {loadingTypes ? (
          <div>Loading agent types...</div>
        ) : (
          <div className="relative">
            <div 
              ref={scrollContainerRef}
              className="flex-1 overflow-y-auto space-y-4 px-2 [&::-webkit-scrollbar]:hidden max-h-[60vh]"
              style={{
                scrollbarWidth: 'none',
                msOverflowStyle: 'none'
              }}
            >
            {generalError && (
              <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                <p className="text-sm text-destructive">{generalError}</p>
              </div>
            )}
            
            <div className="flex flex-col gap-1">
              <Label htmlFor="agent-name">Name</Label>
              <Input 
                id="agent-name" 
                placeholder="Name" 
                value={name} 
                onChange={e => setName(e.target.value)}
                className={fieldErrors.name ? "border-destructive" : ""}
              />
              {fieldErrors.name && (
                <p className="text-xs text-destructive">{fieldErrors.name}</p>
              )}
            </div>
            
            <div className="flex flex-col gap-1">
              <Label htmlFor="agent-type">Type</Label>
              <Select value={type} onValueChange={setType}>
                <SelectTrigger id="agent-type" className={fieldErrors.type ? "border-destructive" : ""}>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  {agentTypes.map(t => (
                    <SelectItem key={t.key} value={t.key}>{t.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {fieldErrors.type && (
                <p className="text-xs text-destructive">{fieldErrors.type}</p>
              )}
            </div>
            
            {type && (
              <AgentConfigurationForm
                agentConfigSections={agentConfigSections}
                openSections={openSections}
                setOpenSections={setOpenSections}
                config={config}
                setConfig={setConfig}
                fieldErrors={fieldErrors}
              />
            )}
            </div>
            {showFade && (
              <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-background to-transparent pointer-events-none"></div>
            )}
          </div>
        )}
        
        <DialogFooter className="flex-shrink-0">
          <Button onClick={handleClose} disabled={submitting}>Cancel</Button>
          <Button disabled={!name || !type || submitting} onClick={handleSubmit}>
            {submitting ? (agent ? "Saving..." : "Creating...") : (agent ? "Save" : "Create")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
