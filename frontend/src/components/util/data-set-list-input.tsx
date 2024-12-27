import { DataSet } from "@/lib/types.ts";
import { ScrollArea } from "@/components/ui/scroll-area.tsx";
import { UseFormReturn } from "react-hook-form";
import { FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { Checkbox } from "@/components/ui/checkbox.tsx";

export interface DataSetListInputProps {
  availableDataSets: DataSet[];
  name: string;
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function DataSetListInput({ availableDataSets, name, form }: DataSetListInputProps) {
  return (
    <ScrollArea className="h-[200px] w-full rounded-md border px-4 py-2">
      <div className="space-y-2">
        {availableDataSets.map((dataSet) => {
          return (
            <FormField
              name={name}
              control={form.control}
              render={(({ field }) => {
                return (
                  <FormItem
                    key={dataSet.id}
                    className="flex flex-row items-center space-x-3 space-y-0"
                  >
                    <FormControl>
                      <Checkbox
                        checked={field.value?.includes(dataSet.id)}
                        onCheckedChange={(checked) => {
                        return checked
                          ? field.onChange([...field.value, dataSet.id])
                          : field.onChange(
                            field.value?.filter(
                              (value: number) => value !== dataSet.id
                            )
                          )
                      }}/>
                    </FormControl>
                    <FormLabel className="text-sm font-normal">
                      {dataSet.name}
                    </FormLabel>
                  </FormItem>
                )
              })}
            />
          )
        })}
      </div>
    </ScrollArea>
  )
}
