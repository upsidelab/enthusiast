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
  HelpCircleIcon, 
  SparklesIcon,
  LinkIcon
} from "lucide-react";
import { UserMenu } from "@/components/navigation/user-menu.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";

export function MainSidebar() {
  const { account, dataSetId } = useApplicationContext()!;
  const { isLoadingAgents } = useApplicationContext()!;
  const { availableAgents } = useApplicationContext()!;


  const synchronizeItems: SidebarSectionItemProps[] = [
    {
      title: "Sources",
      link: `/data-sets/${dataSetId}/sources`,
      key: "sources",
      icon: <LinkIcon />
    },
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
    }
  ];

  const askItems: SidebarSectionItemProps[] = [
    ...(isLoadingAgents ? [] : availableAgents.map(agent => ({
      title: agent.name,
      link: `/data-sets/${dataSetId}/chat/new/${encodeURIComponent(agent.id)}`,
      key: agent.id.toString(),
      icon: <BotMessageSquareIcon />
    }))),
    {
      title: "History",
      link: `/data-sets/${dataSetId}/history`,
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
    },
    {
      title: "Service Accounts",
      link: "/service-accounts",
      key: "service-accounts",
      icon: <PlugZapIcon />
    },
    {
      title: "Help",
      link: "https://upsidelab.io/tools/enthusiast/docs",
      key: "help",
      icon: <HelpCircleIcon />,
      children: [
        {
          title: "Getting Started",
          link: "https://upsidelab.io/tools/enthusiast/docs/category/getting-started/",
          key: "documentation-getting-started",
          icon: <SparklesIcon />
        },
        {
          title: "API Documentation",
          link: `${import.meta.env.VITE_API_BASE}/api/docs`,
          key: "api-documentation",
          icon: <BookTextIcon />
        }
      ]
    },
  ];
  const configureItems: SidebarSectionItemProps[] = [
      {
      title: "Agents",
      link: "/agents",
      key: "agents",
      icon: <BotMessageSquareIcon />
    },
  ]

  return (
    <Sidebar>
      <SidebarHeader>
        <DataSetSelector />
      </SidebarHeader>
      <SidebarContent>
        <MainSidebarSection title="Ask" items={askItems} />
        <MainSidebarSection title="Configure" items={configureItems} />
        <MainSidebarSection title="Synchronize" items={synchronizeItems} />
        {account && account.isStaff && (
          <>
            <MainSidebarSection className="mt-auto" title="Manage" items={manageItems} />
          </>
        )}
      </SidebarContent>
      <SidebarFooter>
        <UserMenu />
      </SidebarFooter>
    </Sidebar>
  );
}
