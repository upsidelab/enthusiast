import { useEffect } from "react";
import { WidgetProps } from "@rjsf/utils";
import { JSONEditor } from "@/components/ui/json-editor.tsx";

function objectToJsonString(obj: Record<string, unknown>): string | null {
  const hasNumericKeys = Object.keys(obj).some((k) => /^\d+$/.test(k));
  if (!hasNumericKeys) return null;
  const real = Object.fromEntries(Object.entries(obj).filter(([k]) => !/^\d+$/.test(k)));
  return JSON.stringify(real, null, 2);
}

function toDisplayValue(
  value: unknown,
  isStringJson: boolean
): string | Record<string, unknown> {
  if (value == null) return "{}";
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    if (isStringJson) {
      const str = objectToJsonString(value as Record<string, unknown>);
      return str ?? JSON.stringify(value, null, 2);
    }
    return value as Record<string, unknown>;
  }
  return String(value);
}

export function JsonEditorWidget(props: WidgetProps) {
  const { value, onChange, label, rawErrors, schema } = props;
  const error = rawErrors?.length ? rawErrors[0] : undefined;
  const s = schema as { type?: string; contentMediaType?: string };
  const isStringJson =
    s?.type === "string" || s?.contentMediaType === "application/json";

  const displayValue = toDisplayValue(value, isStringJson);

  useEffect(() => {
    if (isStringJson && typeof value === "object" && value !== null) {
      const str = objectToJsonString(value as Record<string, unknown>);
      if (str) onChange(str);
    }
  }, [isStringJson, value, onChange]);

  const handleChange = (jsonString: string) => {
    if (jsonString.trim() === "") {
      onChange(null);
      return;
    }
    if (isStringJson) {
      onChange(jsonString);
      return;
    }
    try {
      const parsed = JSON.parse(jsonString) as Record<string, unknown>;
      onChange(parsed);
    } catch {
      onChange(jsonString);
    }
  };

  return (
    <JSONEditor
      value={displayValue}
      onChange={handleChange}
      label={label}
      error={error}
    />
  );
}
