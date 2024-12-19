import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Check, ChevronsUpDown } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList
} from "@/components/ui/command.tsx";
import { cn } from "@/lib/utils.ts";
import { User } from "@/lib/types.ts";
import { useState } from "react";

export interface AddUserSelectorProps {
  availableUsers: User[];
  onSubmit: (newUser: User) => void;
}

export function AddUserSelector({ availableUsers, onSubmit }: AddUserSelectorProps) {
  const [open, setOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | undefined>(undefined);

  const handleSubmit = () => {
    if (!selectedUser) {
      return;
    }

    onSubmit(selectedUser);
    setSelectedUser(undefined);
  };

  return (
    <div className="flex space-x-4">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-[400px] justify-between"
          >
            {selectedUser
              ? selectedUser.email
              : "Select user..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-0">
          <Command>
            <CommandInput placeholder="Search by email..." />
            <CommandList>
              <CommandEmpty>No users found.</CommandEmpty>
              <CommandGroup>
                {availableUsers.map((user) => (
                  <CommandItem
                    key={user.email}
                    value={user.email}
                    onSelect={() => {
                      setSelectedUser(user);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        selectedUser?.id === user.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {user.email}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      <Button variant="default" onClick={handleSubmit} disabled={!selectedUser}>Add</Button>
    </div>
  )
}
