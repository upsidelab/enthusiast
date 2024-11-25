import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader } from "@/components/ui/sidebar.tsx";
import { DataSetSelector } from "@/components/Navigation/DataSetSelector.tsx";
import { MainSidebarSection, SidebarSectionItemProps } from "@/components/Navigation/MainSidebarSection.tsx";
import { BookOpenIcon, BotMessageSquareIcon, FileTextIcon, PlugZapIcon } from "lucide-react";
import { UserMenu } from "@/components/Navigation/UserMenu.tsx";

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
    title: "Campaign",
    link: "/campaign",
    key: "campaign",
    icon: <BotMessageSquareIcon />
  }
];

const integrateItems: SidebarSectionItemProps[] = [
  {
    title: "API Connection",
    link: "/api-connection",
    key: "api-connection",
    icon: <PlugZapIcon />
  }
];

export function MainSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        <DataSetSelector />
      </SidebarHeader>
      <SidebarContent>
        <MainSidebarSection title="Synchronize" items={synchronizeItems} />
        <MainSidebarSection title="Ask" items={askItems} />
        <MainSidebarSection title="Integrate" items={integrateItems} />
      </SidebarContent>
      <SidebarFooter>
        <UserMenu />
      </SidebarFooter>
    </Sidebar>
  )
}
