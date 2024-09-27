import { MainNav } from "@/components/Navigation/MainNav.tsx";
import { DataSetSelector } from "@/components/Navigation/DataSetSelector.tsx";
import { UserMenu } from "@/components/Navigation/UserMenu.tsx";

export function MainMenu() {
  return (
    <div className="hidden flex-col md:flex">
      <div className="border-b">
        <div className="flex h-16 items-center px-4">
          <DataSetSelector className="w-1/6" />
          <MainNav className="mx-6" />
          <div className="ml-auto flex items-center space-x-4">
            <UserMenu />
          </div>
        </div>
      </div>
    </div>
  )
}
