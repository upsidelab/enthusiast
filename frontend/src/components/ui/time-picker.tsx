import * as React from "react";
import { Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface TimePickerProps {
  value?: string;
  onChange?: (time: string) => void;
}

export function TimePicker({ value, onChange }: TimePickerProps) {
  const [hour, setHour] = React.useState<string>("");
  const [minute, setMinute] = React.useState<string>("");
  const [period, setPeriod] = React.useState<"AM" | "PM">("AM");
  const [isOpen, setIsOpen] = React.useState(false);

  const hours = Array.from({ length: 12 }, (_, i) => (i + 1).toString().padStart(2, "0"));
  const minutes = Array.from({ length: 60 }, (_, i) => i.toString().padStart(2, "0"));

  const formatTime = React.useCallback(() => {
    if (!hour || !minute) return "";
    return `${hour}:${minute} ${period}`;
  }, [hour, minute, period]);

  React.useEffect(() => {
    if (value) {
      const [time, period] = value.split(" ");
      const [hour, minute] = time.split(":");
      setHour(hour);
      setMinute(minute);
      setPeriod(period as "AM" | "PM");
    }
  }, [value]);

  React.useEffect(() => {
    const formattedTime = formatTime();
    if (onChange) {
      onChange(formattedTime);
    }
  }, [formatTime, onChange]);

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant={"outline"} className={cn("w-[200px] justify-start text-left font-normal transition-all", !hour && "text-muted-foreground")}>
          <Clock className="mr-2 h-4 w-4" />
          {formatTime() || "Select time"}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[320px] p-4" align="start">
        <div className="flex items-center gap-3">
          <Select value={hour} onValueChange={setHour}>
            <SelectTrigger className="w-[85px]">
              <SelectValue placeholder="Hour" />
            </SelectTrigger>
            <SelectContent position="popper">
              <ScrollArea className="h-[200px]">
                {hours.map((hour) => (
                  <SelectItem key={hour} value={hour}>
                    {hour}
                  </SelectItem>
                ))}
              </ScrollArea>
            </SelectContent>
          </Select>

          <Select value={minute} onValueChange={setMinute}>
            <SelectTrigger className="w-[85px]">
              <SelectValue placeholder="Min" />
            </SelectTrigger>
            <SelectContent position="popper">
              <ScrollArea className="h-[200px]">
                {minutes.map((minute) => (
                  <SelectItem key={minute} value={minute}>
                    {minute}
                  </SelectItem>
                ))}
              </ScrollArea>
            </SelectContent>
          </Select>

          <Select value={period} onValueChange={(value: "AM" | "PM") => setPeriod(value)}>
            <SelectTrigger className="w-[85px]">
              <SelectValue placeholder="AM/PM" />
            </SelectTrigger>
            <SelectContent position="popper">
              <SelectItem value="AM">AM</SelectItem>
              <SelectItem value="PM">PM</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Separator className="my-4" />

        <div className="grid grid-cols-4 gap-2">
          {["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"].map((quickTime) => (
            <Button
              key={quickTime}
              variant="outline"
              size="sm"
              className={cn("text-xs transition-colors", formatTime() === quickTime && "border-primary bg-primary/10")}
              onClick={() => {
                const [time, period] = quickTime.split(" ");
                const [hour, minute] = time.split(":");
                setHour(hour);
                setMinute(minute);
                setPeriod(period as "AM" | "PM");
              }}
            >
              {quickTime}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
