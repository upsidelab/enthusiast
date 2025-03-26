import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader } from "@/components/ui/sidebar.tsx";
import { DataSetSelector } from "@/components/navigation/data-set-selector.tsx";
import { MainSidebarSection, SidebarSectionItemProps } from "@/components/navigation/main-sidebar-section.tsx";
import {
  BookOpenIcon,
  BotMessageSquareIcon,
  DatabaseIcon,
  FileTextIcon,
  BookTextIcon,
  HistoryIcon,
  PlugZapIcon,
  UserIcon,
  FolderSyncIcon
} from "lucide-react";
import { UserMenu } from "@/components/navigation/user-menu.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";

export function MainSidebar() {
  const { account, dataSetId } = useApplicationContext()!;

  const synchronizeItems: SidebarSectionItemProps[] = [
    {
      title: "Products",
      link: `/data-sets/${dataSetId}/products`,
      key: "products",
      icon: <BookOpenIcon />
    },
    {
      title: "Documents",
      link: `/data-sets/${dataSetId}/documents`,
      key: "documents",
      icon: <FileTextIcon />
    },
    account && account.isStaff ? {
      title: "Sync History",
      link: `/data-sets/${dataSetId}/sync-history`,
      key: "sync-history",
      icon: <FolderSyncIcon />
    } : null
  ].filter(Boolean) as SidebarSectionItemProps[];

  const askItems: SidebarSectionItemProps[] = [
    {
      title: "Chat",
      link: `/data-sets/${dataSetId}/chat`,
      key: "chat",
      icon: <BotMessageSquareIcon />
    },
    {
      title: "History",
      link: `/data-sets/${dataSetId}/history`,
      key: "history",
      icon: <HistoryIcon />
    }
  ];

  const integrateItems: SidebarSectionItemProps[] = [
    {
      title: "API Documentation",
      link: `${import.meta.env.VITE_API_BASE}/api/docs`,
      key: "api-documentation",
      icon: <BookTextIcon />
    }
  ];

  const manageItems: SidebarSectionItemProps[] = [
    {
      title: "Data Sets",
      link: "/data-sets",
      key: "data-sets",
      icon: <DatabaseIcon />
    },
    {
      title: "Users",
      link: "/users",
      key: "users",
      icon: <UserIcon />
    },
    {
      title: "Service Accounts",
      link: "/service-accounts",
      key: "service-accounts",
      icon: <PlugZapIcon />
    }
  ];

  return (
    <Sidebar>
      <SidebarHeader>
        <DataSetSelector />
      </SidebarHeader>
      <SidebarContent>
        <MainSidebarSection title="Synchronize" items={synchronizeItems} />
        <MainSidebarSection title="Ask" items={askItems} />
        <MainSidebarSection title="Integrate" items={integrateItems} />
        {account && account.isStaff && (
          <>
            <MainSidebarSection title="Manage" items={manageItems} />
          </>
        )}
      </SidebarContent>
      <SidebarFooter>
        <UserMenu />
      </SidebarFooter>
    </Sidebar>
  );
}
