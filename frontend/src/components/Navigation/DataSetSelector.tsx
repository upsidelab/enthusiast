import { ChevronsUpDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent, DropdownMenuItem,
  DropdownMenuLabel, DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";
import { HTMLAttributes, useEffect, useState } from "react";
import { cn } from "@/lib/utils.ts";
import { ApiClient, DataSet } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";

const api = new ApiClient(authenticationProviderInstance);

export function DataSetSelector({className}: HTMLAttributes<HTMLElement>) {
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const { dataSetId, setDataSetId } = useApplicationContext()!;

  const activeDataSet = () => {
    return dataSets.find((e) => e.id === dataSetId);
  };

  useEffect(() => {
    const fetchData = async () => {
      const apiDataSets = await api.getDataSets();
      setDataSets(apiDataSets);
      if (!apiDataSets.find((e) => e.id === dataSetId)) {
        setDataSetId(apiDataSets[0]?.id || null);
      }
    };

    fetchData();
  }, []);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className={cn("w-1/5 rounded-md ring-ring hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 data-[state=open]:bg-accent", className)}>
        <div className="flex items-center gap-1.5 overflow-hidden px-2 py-1.5 text-left text-sm transition-all">
          <div className="line-clamp-1 flex-1 pr-2 font-medium">
            {activeDataSet()?.name || ''}
          </div>
          <ChevronsUpDown className="ml-auto h-4 w-4 text-muted-foreground/50"/>
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className="w-64"
        align="start"
        side="bottom"
        sideOffset={4}
      >
        <DropdownMenuLabel className="text-xs text-muted-foreground">
          Data Sets
        </DropdownMenuLabel>
        {dataSets.length === 0 ? (
          <DropdownMenuItem disabled className="text-muted-foreground">
            No data sets available
          </DropdownMenuItem>
        ) : (
          dataSets.map((dataSet) => (
            <DropdownMenuItem
              key={dataSet.name}
              onClick={() => setDataSetId(dataSet.id)}
              className="items-start gap-2 px-1.5"
            >
              <div className="grid flex-1 leading-tight">
                <div className="line-clamp-1 font-medium">{dataSet.name}</div>
              </div>
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}