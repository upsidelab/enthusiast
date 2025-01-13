import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";
import { Avatar, AvatarFallback } from "@/components/ui/avatar.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { ApiClient } from "@/lib/api.ts";
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function UserMenu() {
  const navigate = useNavigate();
  const logout = () => {
    authenticationProviderInstance.logout();
    navigate("/login");
  };
  const { account, setAccount } = useApplicationContext()!;

  const userName = () => {
    if (!account) {
      return 'User';
    }

    const components = account.email.split('@');
    return components[0].toUpperCase().slice(0, 1) + components[0].slice(1);
  };

  const email = () => {
    if (!account) {
      return 'Email';
    }

    return account.email;
  }

  const initial = () => {
    if (!account) {
      return 'U';
    }

    return account.email[0].toUpperCase();
  }

  useEffect(() => {
    const ensureAccount = async () => {
      if (!account) {
        const account = await api.getAccount();
        setAccount(account);
      }
    };

    ensureAccount();
  }, [account, setAccount]);

  return (
    <SidebarMenu>
      <SidebarMenuItem>
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton
          size="lg"
          className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
          >
          <Avatar className="h-8 w-8 rounded-lg">
            <AvatarFallback>{initial()}</AvatarFallback>
          </Avatar>
          <div className="grid flex-1 text-left test-sm leading-tight">
            <span className="truncate font-semibold">{userName()}</span>
            <span className="truncate text-xs">{email()}</span>
          </div>

        </SidebarMenuButton>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">
              {userName()}
            </p>
            <p className="text-xs leading-none text-muted-foreground">
              {account?.email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout}>
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
