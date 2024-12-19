import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader } from "@/components/ui/sidebar.tsx";
import { DataSetSelector } from "@/components/Navigation/DataSetSelector.tsx";
import { MainSidebarSection, SidebarSectionItemProps } from "@/components/Navigation/MainSidebarSection.tsx";
import {
  BookOpenIcon,
  BotMessageSquareIcon,
  DatabaseIcon,
  FileTextIcon,
  BookTextIcon,
  HistoryIcon,
  PlugZapIcon,
  UserIcon
} from "lucide-react";
import { UserMenu } from "@/components/Navigation/UserMenu.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";

export function MainSidebar() {
  const { account } = useApplicationContext()!;

  const synchronizeItems: SidebarSectionItemProps[] = [
    {
      title: "Products",
      link: "/products",
      key: "products",
      icon: <BookOpenIcon />
    },
    {
      title: "Documents",
      link: "/documents",
      key: "documents",
      icon: <FileTextIcon />
    }
  ];

  const askItems: SidebarSectionItemProps[] = [
    {
      title: "Chat",
      link: "/ask/chat",
      key: "chat",
      icon: <BotMessageSquareIcon />
    },
    {
      title: "History",
      link: "/ask/history",
      key: "history",
      icon: <HistoryIcon />
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
    }
  ];

  const integrateItems: SidebarSectionItemProps[] = [
    {
      title: "API Connection",
      link: "/api-connection",
      key: "api-connection",
      icon: <PlugZapIcon />
    },
    {
      title: "Documentation",
      link: `${import.meta.env.VITE_API_BASE}/api/docs`,
      key: "documentation",
      icon: <BookTextIcon />
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
        {account && account.isStaff && (
          <>
            <MainSidebarSection title="Integrate" items={integrateItems} />
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