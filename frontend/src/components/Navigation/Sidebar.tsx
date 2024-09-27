import { SidebarSection, SidebarSectionItemProps } from "@/components/Navigation/SidebarSection.tsx";

export function Sidebar() {
  const synchronizeItems: SidebarSectionItemProps[] = [
    {
      title: "Products",
      link: "/products",
      key: "products"
    },
    {
      title: "Content",
      link: "/content",
      key: "content"
    }
  ];

  const createItems: SidebarSectionItemProps[] = [
    {
      title: "Campaign",
      link: "/campaign",
      key: "campaign"
    }
  ];

  const integrateItems: SidebarSectionItemProps[] = [
    {
      title: "API Connection",
      link: "/api-connection",
      key: "api-connection"
    }
  ];

  return (
    <div className="pb-12">
      <div className="space-y-4 py-4">
        <SidebarSection title="Synchronize" items={synchronizeItems} />
        <SidebarSection title="Create" items={createItems} />
        <SidebarSection title="Integrate" items={integrateItems} />
      </div>
    </div>
  )
}
