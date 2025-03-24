import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { useNavigate } from "react-router-dom";
import { DataSet } from "@/lib/types.ts";
import { useState, useEffect } from "react";
import { CheckCircle, XCircle, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { NewScheduleModal } from "@/components/data-sets/sync-schedule/new-schedule-modal.tsx";

const api = new ApiClient(authenticationProviderInstance);

const SyncStatus = "success" | "error" | "idle" | "syncing";

interface SyncInfo {
  lastSyncTime: Date | null;
  status: SyncStatus;
  errorMessage?: string;
}

export function DataSetList() {
  const {dataSets} = useApplicationContext()!;
  const navigate = useNavigate();
  const [syncInfo, setSyncInfo] = useState<SyncInfo>({
    lastSyncTime: null,
    status: "idle",
  });

  useEffect(() => {
    const fetchLastSyncInfo = async () => {
      try {
        const lastSyncData = await api.dataSets().getLastSynchronization();
        setSyncInfo({
          lastSyncTime: new Date(lastSyncData.timestamp),
          status: lastSyncData.status,
          errorMessage: lastSyncData.error_message,
        });
      } catch (error) {
      }
  };

  fetchLastSyncInfo();
}, []);

  const handleSyncAllSources = async () => {
    try {
      setSyncInfo((prev) => ({ ...prev, status: "syncing" }));
      await api.dataSets().syncAllSources();
      setSyncInfo({
        lastSyncTime: new Date(),
        status: "success",
      });
      toast.success("All sources have been synchronized successfully.");
    } catch (error) {
      setSyncInfo({
        lastSyncTime: new Date(),
        status: "error",
        errorMessage: error instanceof Error ? error.message : "Unknown error occurred",
      });
      toast.error(error instanceof Error ? error.message : "Unknown error occurred");
    }
  };

  const handleSyncDataSetAllSources = async (dataSet: DataSet) => {
    try {
      setSyncInfo((prev) => ({ ...prev, status: "syncing" }));
      await api.dataSets().syncDataSetAllSources(dataSet.id);
      setSyncInfo({
        lastSyncTime: new Date(),
        status: "success",
      });
      toast.success(`Data set ${dataSet.name} has been synchronized successfully.`);
    } catch (error) {
      setSyncInfo({
        lastSyncTime: new Date(),
        status: "error",
        errorMessage: error instanceof Error ? error.message : "Unknown error occurred",
      });
      toast.error(error instanceof Error ? error.message : "Unknown error occurred");
    }
  };

  const formatSyncTime = (date: Date | null) => {
    if (!date) return "Never";
    return date.toLocaleString();
  };

  return (
    <>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Last synchronization:</span>
            {syncInfo.status === "syncing" ? (
              <Badge variant="outline" className="flex items-center gap-1 bg-blue-50 text-blue-700 border-blue-200">
                <Clock className="h-3.5 w-3.5" />
                <span>Syncing...</span>
              </Badge>
            ) : syncInfo.status === "success" ? (
              <Badge variant="outline" className="flex items-center gap-1 bg-green-50 text-green-700 border-green-200">
                <CheckCircle className="h-3.5 w-3.5" />
                <span>{formatSyncTime(syncInfo.lastSyncTime)}</span>
              </Badge>
            ) : syncInfo.status === "error" ? (
              <Badge
                variant="outline"
                className="flex items-center gap-1 bg-red-50 text-red-700 border-red-200"
                title={syncInfo.errorMessage}
              >
                <XCircle className="h-3.5 w-3.5" />
                <span>{formatSyncTime(syncInfo.lastSyncTime)} - Failed</span>
              </Badge>
            ) : (
              <Badge variant="outline" className="flex items-center gap-1">
                <span>{formatSyncTime(syncInfo.lastSyncTime)}</span>
              </Badge>
            )}
          </div>
        </div>
        <div className="flex flex-row justify-end items-center space-x-4">
          <Button variant="default" onClick={() => navigate('/data-sets/new')}>
            New Data Set
          </Button>
        <Button variant="default" onClick={() => handleSyncAllSources() }>Sync All</Button>
        </div>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {dataSets.map((item, index) => (
            <TableRow key={index}>
              <TableCell width="75%">
                {item.name}
              </TableCell>
              <TableCell className="flex space-x-4" width="25%">
                <Button onClick={() => {
                  navigate(`/data-sets/${item.id}/users`)
                }} variant="secondary">Manage Access</Button>
              </TableCell>
              <TableCell>
                <Button onClick={() => {
                  navigate(`/data-sets/${item.id}/catalog-sources`)
                }} variant="secondary">Sources</Button>
              </TableCell>
              <TableCell>
                <Button onClick={() => {
                  handleSyncDataSetAllSources(item)
                }} variant="secondary">Sync</Button>
              </TableCell>
              <TableCell>
                <NewScheduleModal
                  dataSetName={item.name}
                  dataSetId={item.id}
                />
              </TableCell>
             </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}
