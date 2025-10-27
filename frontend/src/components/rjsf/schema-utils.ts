function shouldUseJsonEditor(propSchema: unknown): boolean {
  if (!propSchema || typeof propSchema !== "object") return false;
  const s = propSchema as Record<string, unknown>;
  const type = s.type;
  const contentMediaType = s.contentMediaType as string | undefined;
  if (type === "string" && (contentMediaType === "application/json" || s.format === "json" || s.format === "json-string")) return true;
  if (type !== "object") return false;
  const props = s.properties as Record<string, unknown> | undefined;
  const hasNoNestedProps = !props || typeof props !== "object" || Object.keys(props).length === 0;
  return hasNoNestedProps || s.additionalProperties === true;
}

export function jsonWidgetUiSchema(schema: unknown): { "ui:widget"?: "json" } {
  return shouldUseJsonEditor(schema) ? { "ui:widget": "json" } : {};
}
