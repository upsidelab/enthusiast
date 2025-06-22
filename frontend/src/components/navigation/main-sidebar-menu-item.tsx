import { SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar.tsx";
import { Link, useLocation } from "react-router-dom";
import { SidebarSectionItemProps } from "@/components/navigation/main-sidebar-section.tsx";

export interface MainSidebarMenuItemProps {
  item: SidebarSectionItemProps;
}

export function MainSidebarMenuItem({item}: MainSidebarMenuItemProps) {
  const location = useLocation();

  return (
    <SidebarMenuItem>
      <SidebarMenuButton asChild isActive={location.pathname === item.link}>
        <Link
          to={item.link}
        >
          {item.icon}
          {item.title}
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  )
}
