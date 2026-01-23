import { SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar.tsx";
import { SidebarSectionItemProps } from "@/components/navigation/main-sidebar-section.tsx";

export interface MainSidebarMenuItemProps {
  item: SidebarSectionItemProps;
}

export function MainSidebarMenuSimpleItem({item}: MainSidebarMenuItemProps) {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton disabled={item.disabled}>
        {item.icon}
        {item.title}
      </SidebarMenuButton>
    </SidebarMenuItem>
  )
}
