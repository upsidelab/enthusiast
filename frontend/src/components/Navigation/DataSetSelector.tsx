import { ChevronsUpDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";
import { useEffect, useState } from "react";
import { ApiClient, DataSet } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { SidebarMenuButton } from "@/components/ui/sidebar.tsx";
import logoUrl from "@/assets/logo.png";

const api = new ApiClient(authenticationProviderInstance);

export function DataSetSelector() {
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
  }, [dataSetId, setDataSetId]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton
          size="lg"
          className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
        >
          <div
            className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <img src={logoUrl} alt="Upside" className="size-8 rounded-lg"/>
          </div>
          <div className="flex flex-col gap-0.5 leading-none">
          <span className="font-semibold">Data Set</span>
            <span className="">{activeDataSet()?.name}</span>
          </div>
          <ChevronsUpDown className="ml-auto" />
        </SidebarMenuButton>
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
