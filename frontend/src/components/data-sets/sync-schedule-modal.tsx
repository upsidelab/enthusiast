import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog.tsx";
import { Button } from "@/components/ui/button.tsx";
import { useState, useEffect } from "react";
import { SyncScheduleForm } from "./form/sync-schedule-form.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { SyncSchedule } from "@/lib/types.ts";

const api = new ApiClient(authenticationProviderInstance);

export interface SyncScheduleModalProps {
  dataSetName: string;
  dataSetId: number;
}

export function SyncScheduleModal({ dataSetName, dataSetId }: SyncScheduleModalProps) {
  const [open, setOpen] = useState(false);
  const [initialValues, setInitialValues] = useState<SyncSchedule | null>(null);

  useEffect(() => {
    if (open) {
      const fetchSchedule = async () => {
        try {
          const scheduleData = await api.dataSets().getSyncSchedule(dataSetId);
          setInitialValues(scheduleData);
        } catch {
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
        <SyncScheduleForm dataSetId={dataSetId} onScheduleCreated={() => setOpen(false)} initialValues={initialValues} />
      </DialogContent>
    </Dialog>
  );
}
