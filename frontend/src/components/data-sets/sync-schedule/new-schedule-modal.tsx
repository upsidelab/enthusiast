import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useState } from "react";
import { NewScheduleForm } from "./form/new-schedule-form.tsx";
import { Calendar } from "lucide-react";

export interface NewScheduleModalProps {
  onScheduleCreated: () => void;
  dataSetName: string;
  dataSetId: number;
}

export function NewScheduleModal({ onScheduleCreated, dataSetName, dataSetId }: NewScheduleModalProps) {
  const [open, setOpen] = useState(false);

  const handleScheduleCreated = () => {
    setOpen(false);
    onScheduleCreated();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary">
          <Calendar className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Sync schedule for {dataSetName}</DialogTitle>
        </DialogHeader>
        <NewScheduleForm dataSetId={dataSetId} onScheduleCreated={handleScheduleCreated} />
      </DialogContent>
    </Dialog>
  );
}