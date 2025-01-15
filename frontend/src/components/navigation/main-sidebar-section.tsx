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
import { useApplicationContext } from "@/lib/use-application-context.ts";

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
  const { dataSetId } = useApplicationContext()!;

  return (
    <SidebarGroup>
      <SidebarGroupLabel>{title}</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            return (
              <SidebarMenuItem key={item.key}>
                <SidebarMenuButton asChild isActive={location.pathname === item.link}>
                  <Link
                    to={item.link}
                    target={item.key === 'documentation' ? "_blank" : undefined}
                    reloadDocument={item.link === `/data-sets/${dataSetId}/chat`}
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
