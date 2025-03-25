import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useState, useEffect } from "react";
import { NewScheduleForm } from "./form/new-schedule-form.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface NewScheduleModalProps {
  dataSetName: string;
  dataSetId: number;
}

export function NewScheduleModal({ dataSetName, dataSetId }: NewScheduleModalProps) {
  const [open, setOpen] = useState(false);
  const [initialValues, setInitialValues] = useState(null);

  useEffect(() => {
    if (open) {
      const fetchSchedule = async () => {
        try {
          const scheduleData = await api.dataSets().getSyncSchedule(dataSetId);
          setInitialValues(scheduleData);
        } catch (error) {
          setInitialValues(null);
        }
      };
      fetchSchedule();
    }
  }, [open, dataSetId]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary">
          Schedule
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Sync schedule for {dataSetName}</DialogTitle>
        </DialogHeader>
        <NewScheduleForm dataSetId={dataSetId} onScheduleCreated={() => setOpen(false)} initialValues={initialValues} />
      </DialogContent>
    </Dialog>
  );
}
