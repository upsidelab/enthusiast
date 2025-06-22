import { SidebarMenuButton, SidebarMenuItem, useSidebar } from "@/components/ui/sidebar.tsx";
import { Link, useLocation } from "react-router-dom";
import { SidebarSectionItemProps } from "@/components/navigation/main-sidebar-section.tsx";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";

export interface MainSidebarMenuDropdownItemProps {
  item: SidebarSectionItemProps;
}

export function MainSidebarMenuDropdownItem({ item }: MainSidebarMenuDropdownItemProps) {
  const location = useLocation();
  const { isMobile } = useSidebar();

  return (
    <DropdownMenu>
      <SidebarMenuItem>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton asChild isActive={location.pathname === item.link}>
            <Link
              to={item.link}
            >
              {item.icon}
              {item.title}
            </Link>
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        {item.children &&
          (<DropdownMenuContent
            side={isMobile ? "bottom" : "right"}
            align={isMobile ? "end" : "start"}
            className="min-w-56 rounded-lg"
          >
            {item.children.map((child) => {
              return (
                <DropdownMenuItem asChild key={child.title}>
                  <Link to={child.link}>
                    {child.icon}
                    {child.title}
                  </Link>
                </DropdownMenuItem>
              )
            })}
          </DropdownMenuContent>)}
      </SidebarMenuItem>
    </DropdownMenu>
  )
}
