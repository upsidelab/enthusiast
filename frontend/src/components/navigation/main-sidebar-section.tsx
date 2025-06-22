import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
} from "@/components/ui/sidebar.tsx";
import { ReactNode } from "react";
import { MainSidebarMenuItem } from "@/components/navigation/main-sidebar-menu-item.tsx";
import { MainSidebarMenuDropdownItem } from "@/components/navigation/main-sidebar-menu-dropdown-item.tsx";

export interface SidebarSectionItemProps {
  title: string;
  link: string;
  key: string;
  icon: ReactNode,
  children?: SidebarSectionItemProps[];
}

export interface SidebarSectionProps {
  title: string;
  items: SidebarSectionItemProps[];
  className?: string;
}

export function MainSidebarSection({ title, items, className }: SidebarSectionProps) {
  return (
    <SidebarGroup className={className}>
      <SidebarGroupLabel>{title}</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            if (item.children) {
              return <MainSidebarMenuDropdownItem key={item.key} item={item}/>
            } else {
              return <MainSidebarMenuItem key={item.key} item={item}/>
            }
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
