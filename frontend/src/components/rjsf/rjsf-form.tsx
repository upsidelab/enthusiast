/* eslint-disable react-refresh/only-export-components -- file exports RjsfForm + shared utils (buildDefaultFormDataFromSections) */
import { useMemo } from "react";
import Form from "@rjsf/core";
import type { ErrorSchema, RJSFSchema, UiSchema } from "@rjsf/utils";
import { createSchemaUtils } from "@rjsf/utils";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown, ChevronRight } from "lucide-react";
export type RjsfFormChoice = { [key: string]: RJSFSchema | string | undefined } & { $defs?: Record<string, RJSFSchema>; tools?: RJSFSchema[] };
import { rjsfTemplates } from "./rjsf-theme";
import { rjsfWidgets } from "./rjsf-theme";
import { WrappedAnyOfField, WrappedOneOfField, getUnionOptionUiSchema, isUnionSchema } from "./rjsf-multischema-field-template";
import validator from "@rjsf/validator-ajv8";

type SectionSpec = { key: string; schema: RJSFSchema; defs?: Record<string, unknown> };

function shouldUseJsonEditor(propSchema: unknown): boolean {
  if (!propSchema || typeof propSchema !== "object") return false;
  const s = propSchema as Record<string, unknown>;
  const contentMediaType = s.contentMediaType as string | undefined;
  return contentMediaType === "application/json";
}

function jsonWidgetUiSchema(schema: unknown): { "ui:widget"?: "json" } {
  return shouldUseJsonEditor(schema) ? { "ui:widget": "json" } : {};
}

export function buildDefaultFormDataFromSections(
  sectionSpecs: SectionSpec[],
  toolSchemas: RJSFSchema[] | undefined,
): Record<string, unknown> {
  const config: Record<string, unknown> = {};

  for (const { key, schema } of sectionSpecs) {
    if (schema && typeof schema === "object" && !Array.isArray(schema) && Object.keys(schema).length > 0) {
      config[key] = {};
    }
  }

  if (Array.isArray(toolSchemas) && toolSchemas.length > 0) {
    config.tools = toolSchemas.map(() => ({}));
  }

  return config;
}

export function getDefaultFormData(
  choice: RjsfFormChoice,
  sectionKeys: readonly string[]
): Record<string, unknown> {
  const sectionSpecs = sectionKeys.map((key) => ({
    key,
    schema: (choice[key] ?? {}) as RJSFSchema,
  }));
  const toolSchemas = Array.isArray(choice.tools) ? (choice.tools as RJSFSchema[]) : undefined;
  return buildDefaultFormDataFromSections(sectionSpecs, toolSchemas);
}

function buildUiSchema(schema: RJSFSchema, defs?: Record<string, unknown>): UiSchema {
  const ui: Record<string, unknown> = {};
  const rootSchema = {
    $defs: { ...((schema as { $defs?: Record<string, unknown> }).$defs ?? {}), ...(defs ?? {}) },
  } as RJSFSchema;
  const schemaUtils = createSchemaUtils(validator as never, rootSchema);
  const resolved = schemaUtils.retrieveSchema(schema);
  const props = (resolved as { properties?: Record<string, unknown> }).properties;
  if (!props || typeof props !== "object") return ui as UiSchema;

  for (const [propName, propSchema] of Object.entries(props)) {
    const s = propSchema as Record<string, unknown>;
    if (!s || typeof s !== "object") continue;

    const propUi: Record<string, unknown> = { ...jsonWidgetUiSchema(s)};
    if (isUnionSchema(s)) {
      const optionUi = getUnionOptionUiSchema(s);
      if (optionUi) {
        const key = "oneOf" in s ? "oneOf" : "anyOf";
        propUi[key] = optionUi;
      }
    }
    if (Object.keys(propUi).length > 0) ui[propName] = propUi;
  }
  return ui as UiSchema;
}

function fieldErrorsToErrorSchema(
  fieldErrors: Record<string, string>,
  sectionKey: string
): ErrorSchema | undefined {
  const prefix = sectionKey === "tools" ? "tools." : `${sectionKey}.`;
  const entries = Object.entries(fieldErrors).filter(([k]) => k.startsWith(prefix));
  if (entries.length === 0) return undefined;

  const result: Record<string, unknown> = {};
  for (const [key, message] of entries) {
    const suffix = key.slice(prefix.length);
    const parts = suffix.split(".");
    let current: Record<string, unknown> = result;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLast = i === parts.length - 1;
      if (isLast) {
        current[part] = { __errors: [message] };
      } else {
        if (!(part in current) || typeof current[part] !== "object") {
          current[part] = {};
        }
        current = current[part] as Record<string, unknown>;
      }
    }
  }
  return result as ErrorSchema;
}

interface RjsfFormProps {
  choice: RjsfFormChoice;
  config: Record<string, unknown>;
  sectionKeys: readonly string[];
  sectionTitles: Record<string, string>;
  onConfigChange: (key: string, value: unknown) => void;
  fieldErrors: Record<string, string>;
  openSections: Record<string, boolean>;
  onOpenSectionsChange: (sections: Record<string, boolean>) => void;
  showToolsSection?: boolean;
  header?: React.ReactNode;
  emptyMessage?: React.ReactNode;
}

const rjsfFields = {
  AnyOfField: WrappedAnyOfField,
  OneOfField: WrappedOneOfField,
};

export function RjsfForm({
  choice,
  config,
  sectionKeys,
  sectionTitles,
  onConfigChange,
  fieldErrors,
  openSections,
  onOpenSectionsChange,
  showToolsSection = true,
  header,
  emptyMessage,
}: RjsfFormProps) {
  const defs = choice.$defs;
  const hasFieldErrors = Object.keys(fieldErrors).length > 0;
  const toolsCount = showToolsSection && Array.isArray(choice.tools) ? choice.tools.length : 0;

  const sections = useMemo(() => {
    const result: Array<{
      key: string;
      title: string;
      schema: RJSFSchema;
      formData: Record<string, unknown> | Record<string, unknown>[];
      uiSchema: UiSchema;
    }> = [];

    for (const key of sectionKeys) {
      const schema = (choice[key] ?? {}) as RJSFSchema;
      if (!schema || typeof schema !== "object" || Array.isArray(schema) || Object.keys(schema).length === 0) continue;

      const formData = (config[key] ?? {}) as Record<string, unknown>;
      const uiSchema = buildUiSchema(schema, defs);

      result.push({
        key,
        title: sectionTitles[key],
        schema,
        formData,
        uiSchema,
      });
    }

    if (toolsCount > 0) {
      const toolSchemas = choice.tools as RJSFSchema[];
      const toolsFormData = (config.tools ?? []) as Record<string, unknown>[];
      const padded =
        toolsFormData.length >= toolsCount
          ? toolsFormData
          : [...toolsFormData, ...Array.from({ length: toolsCount - toolsFormData.length }, () => ({}))];
      const allToolsEmpty = padded.every(
        (t) => typeof t === "object" && t !== null && Object.keys(t).length === 0
      );
      if (!allToolsEmpty) {
        const toolsSchema: RJSFSchema = {
          type: "array",
          title: "Tools",
          items: Array.isArray(toolSchemas) && toolSchemas.length > 0
            ? (toolSchemas.length === 1 ? toolSchemas[0] : (toolSchemas as RJSFSchema[]))
            : { type: "object" },
        };
        result.push({
          key: "tools",
          title: "Tools",
          schema: toolsSchema,
          formData: padded,
          uiSchema: {},
        });
      }
    }

    return result;
  }, [choice, config, sectionKeys, sectionTitles, defs, toolsCount]);

  const setOpen = (key: string, open: boolean) => {
    onOpenSectionsChange({ ...openSections, [key]: open });
  };
  const openSectionsWithErrors = useMemo(() => {
    const next = { ...openSections };
    let changed = false;
    for (const errKey of Object.keys(fieldErrors)) {
      if (showToolsSection && errKey.startsWith("tools.") && !next.tools) {
        next.tools = true;
        changed = true;
      }
      for (const key of sectionKeys) {
        const prefix = `${key}.`;
        if (errKey.startsWith(prefix) && !next[key]) {
          next[key] = true;
          changed = true;
        }
      }
    }
    if (changed) return next;
    return openSections;
  }, [fieldErrors, openSections, sectionKeys, showToolsSection]);

  const effectiveOpenSections = Object.keys(fieldErrors).length > 0 ? openSectionsWithErrors : openSections;

  if (sections.length === 0) {
    return (
      <div className="space-y-2">
        {header}
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="space-y-2" data-has-field-errors={hasFieldErrors || undefined}>
      {header}
      <div className="space-y-2">
        {sections.map(({ key, title, schema, formData, uiSchema }) => {
          const schemaObj = schema as Record<string, unknown>;
          const schemaDefs = schemaObj.$defs as Record<string, unknown> | undefined;
          const mergedDefs = { ...(schemaDefs ?? {}), ...(defs ?? {}) };
          const rootSchema = {
            ...schemaObj,
            $defs: mergedDefs,
          } as RJSFSchema;
          const isOpen = effectiveOpenSections[key] ?? false;

          const handleChange = ({ formData: newData }: { formData?: Record<string, unknown> | Record<string, unknown>[] }) => {
            onConfigChange(key, newData ?? (key === "tools" ? [] : {}));
          };

          const extraErrors = fieldErrorsToErrorSchema(fieldErrors, key);
          const formUiSchema = {
            ...uiSchema,
            "ui:options": {
              ...((uiSchema as Record<string, unknown>)["ui:options"] as Record<string, unknown> | undefined),
              submitButtonOptions: { norender: true },
              label: false,
            },
          };

          return (
            <Collapsible key={key} open={isOpen} onOpenChange={(o) => setOpen(key, o)}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                  <div className="flex items-center gap-2">
                    {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    <span className="text-sm font-medium text-foreground">{title}</span>
                  </div>
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-4 pt-2 pb-4">
                <div className="pl-2 border-l-2 border-muted">
                  <Form
                    schema={rootSchema}
                    formData={formData}
                    uiSchema={formUiSchema as never}
                    validator={validator as never}
                    templates={rjsfTemplates}
                    widgets={rjsfWidgets}
                    fields={rjsfFields}
                    omitExtraData={false}
                    liveValidate={false}
                    showErrorList={false}
                    onChange={handleChange}
                    extraErrors={extraErrors as never}
                    formContext={{
                      defs: mergedDefs,
                      ...(key === "tools" ? { toolsFormData: formData as Record<string, unknown>[] } : {}),
                    }}
                  />
                </div>
              </CollapsibleContent>
            </Collapsible>
          );
        })}
      </div>
    </div>
  );
}
