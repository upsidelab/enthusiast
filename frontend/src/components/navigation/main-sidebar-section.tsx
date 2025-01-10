import { Link, useLocation } from "react-router-dom";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem
} from "@/components/ui/sidebar.tsx";
import { ReactNode } from "react";

export interface SidebarSectionItemProps {
  title: string;
  link: string;
  key: string;
  icon: ReactNode
}

export interface SidebarSectionProps {
  title: string;
  items: SidebarSectionItemProps[];
}

export function MainSidebarSection({ title, items }: SidebarSectionProps) {
  const location = useLocation();

  return (
    <SidebarGroup>
      <SidebarGroupLabel>{title}</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            return (
              <SidebarMenuItem key={item.key}>
                <SidebarMenuButton asChild isActive={location.pathname.startsWith(item.link)}>
                  <Link
                    to={item.link}
                    target={item.key === 'documentation' ? "_blank" : undefined}
                  >
                    {item.icon}
                    {item.title}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            )
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
