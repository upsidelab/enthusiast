import {
  DropdownMenu,
  DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem,
  DropdownMenuLabel, DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu.tsx";
import { Avatar, AvatarFallback } from "@/components/ui/avatar.tsx";
import { Button } from "@/components/ui/button.tsx";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Link, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { ApiClient } from "@/lib/api.ts";

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
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-8 w-8 rounded-full">
          <Avatar className="h-8 w-8">
            <AvatarFallback>{initial()}</AvatarFallback>
          </Avatar>
        </Button>
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
        <DropdownMenuGroup>
          <DropdownMenuItem asChild>
            <Link to="/billing">
              Billing
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link to="/settings">
              Settings
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout}>
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
