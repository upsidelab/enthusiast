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
import { SourcePlugin } from "@/lib/types.ts";
import { useState } from "react";

export interface AddSourcePluginSelectorProps {
  sourcePlugins: SourcePlugin[];
  onSubmit: (newSourcePlugin: SourcePlugin) => void;
}

export function AddSourcePluginSelector({ sourcePlugins, onSubmit }: AddSourcePluginSelectorProps) {
  const [open, setOpen] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState<SourcePlugin | undefined>(undefined);

  const handleSubmit = () => {
    if (!selectedPlugin) {
      return;
    }

    onSubmit(selectedPlugin);
    setSelectedPlugin(undefined);
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
            {selectedPlugin
              ? selectedPlugin.plugin_name
              : "Select plugin..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-0">
          <Command>
            <CommandInput placeholder="Search by plugin name..." />
            <CommandList>
              <CommandEmpty>No plugins found.</CommandEmpty>
              <CommandGroup>
                {sourcePlugins.map((plugin) => (
                  <CommandItem
                    key={plugin.plugin_name}
                    value={plugin.plugin_name}
                    onSelect={() => {
                        setSelectedPlugin(plugin);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        selectedPlugin?.plugin_name === plugin.plugin_name ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {plugin.plugin_name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      <Button variant="default" onClick={handleSubmit} disabled={!selectedPlugin}>Add</Button>
    </div>
  )
}
