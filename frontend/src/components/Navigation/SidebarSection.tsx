import { Button } from "@/components/ui/button.tsx";
import { Link, useLocation } from "react-router-dom";

export interface SidebarSectionItemProps {
  title: string;
  link: string;
  key: string;
}

export interface SidebarSectionProps {
  title: string;
  items: SidebarSectionItemProps[];
}

export function SidebarSection({ title, items }: SidebarSectionProps) {
  const location = useLocation();

  return (
    <div className="px-3 py-2">
      <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
        {title}
      </h2>
      <div className="space-y-1">
        {items.map((item) => {
          const type: "secondary" | "ghost" = location.pathname === item.link ? "secondary" : "ghost";
          return (
            <Button variant={type} key={item.key} className="w-full justify-start" asChild>
              <Link to={item.link}>
                {item.title}
              </Link>
            </Button>
          )
        })}
      </div>
    </div>
  );
}
