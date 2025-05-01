import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx";
import { UseFormReturn } from "react-hook-form";
import { Calendar } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

export interface ScheduleFrequencyFieldsProps {
  form: UseFormReturn<any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

export function ScheduleFrequencyFields({ form }: ScheduleFrequencyFieldsProps) {
  const frequency = form.watch("frequency");
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  const formDayAbbrev = form.watch("day_of_week");
  const selectedDay =
    days.find((day) => day.substring(0, 3).toLowerCase() === formDayAbbrev) || "Sunday";

  const showDaySelection = frequency === "weekly";

  const selectDay = (day: string) => {
    form.setValue("day_of_week", day.substring(0, 3).toLowerCase());
  };

  return (
    <FormField
      control={form.control}
      name="frequency"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Frequency</FormLabel>
          <FormControl>
            <div className="space-y-8 max-w-md mx-auto p-8 border rounded-xl shadow-sm bg-card">
              <div className="space-y-3">
                <Label htmlFor="sync-frequency" className="text-base font-medium">
                  Synchronization Frequency
                </Label>
                <Select
                  // Removed fallback value
                  value={field.value}
                  onValueChange={(value) => {
                    field.onChange(value);
                  }}
                >
                  <SelectTrigger id="sync-frequency" className="w-full">
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Once a week</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {showDaySelection && (
                <div className="space-y-4">
                  <Label className="flex items-center gap-2 text-base font-medium">
                    <Calendar className="h-5 w-5" />
                    Select day for synchronization
                  </Label>

                  <div className="grid grid-cols-7 gap-3">
                    {days.map((day) => (
                      <button
                        key={day}
                        type="button"
                        onClick={() => selectDay(day)}
                        className={cn(
                          "aspect-square rounded-full flex flex-col items-center justify-center transition-all",
                          selectedDay === day
                            ? "bg-primary text-primary-foreground ring-2 ring-primary ring-offset-2"
                            : "bg-muted hover:bg-muted/80"
                        )}
                      >
                        <span className="text-xs font-medium">{day.substring(0, 1)}</span>
                      </button>
                    ))}
                  </div>

                  <div className="flex items-center justify-between mt-4 px-2">
                    <div className="text-sm font-medium">Selected day:</div>
                    <div className="text-sm bg-primary/10 text-primary px-3 py-1 rounded-full font-medium">
                      {selectedDay}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </FormControl>
          <FormMessage />
          <FormDescription>
            Specify the frequency of the synchronization.
          </FormDescription>
        </FormItem>
      )}
    />
  );
}
