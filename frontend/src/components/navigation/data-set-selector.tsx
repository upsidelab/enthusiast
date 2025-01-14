import { ChevronsUpDown, ListIcon, PlusCircleIcon } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";
import { useEffect } from "react";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { SidebarMenuButton } from "@/components/ui/sidebar.tsx";
import logoUrl from "@/assets/logo.png";
import logoSvgUrl from '@/assets/logo.svg';
import { Separator } from "@/components/ui/separator.tsx";
import { useNavigate } from "react-router-dom";

const api = new ApiClient(authenticationProviderInstance);

export function DataSetSelector() {
  const { dataSets, setDataSets, dataSetId, setDataSetId, account } = useApplicationContext()!;
  const navigate = useNavigate();

  const activeDataSet = () => {
    return dataSets.find((e) => e.id === dataSetId);
  };

  useEffect(() => {
    const fetchData = async () => {
      const apiDataSets = await api.dataSets().getDataSets();
      setDataSets(apiDataSets);
      if (!apiDataSets.find((e) => e.id === dataSetId)) {
        setDataSetId(apiDataSets[0]?.id || null);
      }
    };

    fetchData();
  }, [dataSetId, setDataSetId, setDataSets]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton
          size="lg"
          className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
        >
          <div
            className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <img src={logoUrl} srcSet={logoSvgUrl} alt="Enthusiast" className="size-8 rounded-lg"/>
          </div>
          <div className="flex flex-col gap-0.5 leading-none">
            <span className="font-semibold">Enthusiast</span>
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
              onClick={() => setDataSetId(dataSet.id || null)}
              className="items-start gap-2 px-1.5"
            >
              <div className="grid flex-1 leading-tight">
                <div className="line-clamp-1 font-medium">{dataSet.name}</div>
              </div>
            </DropdownMenuItem>
          ))
        )}
        {account && account.isStaff &&
          <>
            <Separator className="my-2"/>
            <DropdownMenuItem
              key="new"
              onClick={() => navigate('/data-sets/new')}
              className="gap-2 px-1.5"
            >
              <PlusCircleIcon className="size-4" />
              New
            </DropdownMenuItem>
            <DropdownMenuItem
              key="manage"
              onClick={() => navigate('/data-sets')}
              className="gap-2 px-1.5"
            >
              <ListIcon className="size-4" />
              Manage
            </DropdownMenuItem>
          </>
        }
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
