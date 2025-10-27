/* eslint-disable react-refresh/only-export-components -- file exports field templates + getUnionOptionUiSchema, isUnionSchema */
import type { ComponentType } from "react";
import { useCallback, useMemo, useRef } from "react";
import { getDefaultRegistry } from "@rjsf/core";
import type {
  ErrorSchema,
  FieldPathList,
  FieldProps,
  FormContextType,
  RJSFSchema,
  StrictRJSFSchema,
} from "@rjsf/utils";

const ANY_OF_KEY = "anyOf";
const ONE_OF_KEY = "oneOf";

function isNoneOption(opt: Record<string, unknown>): boolean {
  if (!opt || typeof opt !== "object") return false;
  const t = opt.type;
  if (t === "null") return true;
  if (opt.const === null) return true;
  const title = opt.title;
  if (typeof title === "string" && title.toLowerCase() === "none") {
    if (t === "null" || t === undefined) return true;
    if (Array.isArray(t) && t.length === 1 && t[0] === "null") return true;
  }
  if (Array.isArray(t) && t.length === 1 && t[0] === "null") return true;
  return false;
}

function getSchemaValueType(schema: Record<string, unknown>): string | undefined {
  const t = schema.type;
  if (Array.isArray(t)) return (t.find((x) => x !== "null") ?? t[0]) as string;
  return t as string | undefined;
}

function isEmptyValue(schema: Record<string, unknown>, value: unknown): boolean {
  if (value === undefined || value === null) return true;
  const t = getSchemaValueType(schema);
  if (t === "string") return typeof value === "string" && value.trim() === "";
  if (t === "number" || t === "integer") return false;
  if (t === "object") return typeof value === "object" && (value === null || Object.keys(value as object).length === 0);
  if (t === "array") return Array.isArray(value) && value.length === 0;
  return false;
}

export function isOptionalUnionSchema(
  schema: Record<string, unknown>,
  resolveSchema: (s: Record<string, unknown>, formData?: unknown) => RJSFSchema | null
): boolean {
  const options = (schema[ONE_OF_KEY] ?? schema[ANY_OF_KEY]) as Record<string, unknown>[] | undefined;
  if (!Array.isArray(options) || options.length !== 2) return false;
  const resolved = options.map((opt) => resolveSchema(opt as Record<string, unknown>));
  const noneCount = resolved.filter((r) => r && isNoneOption(r as Record<string, unknown>)).length;
  return noneCount === 1;
}

function getOptionalUnionValueOption<T>(
  schema: Record<string, unknown>,
  keyOf: "oneOf" | "anyOf",
  resolveSchema: (s: Record<string, unknown>, formData?: T) => RJSFSchema | null
): { valueSchema: RJSFSchema; valueIndex: number } | null {
  const options = (schema[keyOf] ?? []) as Record<string, unknown>[];
  if (!Array.isArray(options) || options.length !== 2) return null;
  const resolved = options.map((opt) => resolveSchema(opt as Record<string, unknown>));
  const noneIdx = resolved.findIndex((r) => r && isNoneOption(r as Record<string, unknown>));
  const valueIdx = noneIdx === 0 ? 1 : 0;
  const valueSchema = resolved[valueIdx];
  if (!valueSchema) return null;
  return { valueSchema, valueIndex: valueIdx };
}

export function getUnionOptionUiSchema(schema: Record<string, unknown>): Record<string, unknown>[] | null {
  const options = (schema[ONE_OF_KEY] ?? schema[ANY_OF_KEY]) as Record<string, unknown>[] | undefined;
  if (!Array.isArray(options) || options.length === 0) return null;
  return options.map((opt) => {
    const title = (opt?.title ?? opt?.const ?? "Option") as string;
    return { title };
  });
}

export function isUnionSchema(propSchema: Record<string, unknown>): boolean {
  const options = propSchema.oneOf ?? propSchema.anyOf;
  return Array.isArray(options) && options.length > 0;
}

const defaultRegistry = getDefaultRegistry();
const DefaultAnyOfField = defaultRegistry.fields.AnyOfField;
const DefaultOneOfField = defaultRegistry.fields.OneOfField;

function useStableMergedUiSchema(
  uiSchema: Record<string, unknown>,
  schema: Record<string, unknown>,
  keyOf: "oneOf" | "anyOf"
): Record<string, unknown> {
  const optionUi = useMemo(() => getUnionOptionUiSchema(schema), [schema]);
  const optionKey = useMemo(() => (optionUi ? JSON.stringify(optionUi) : ""), [optionUi]);
  const mergedRef = useRef<Record<string, unknown>>({});
  const keyRef = useRef<string>("");
  if (!optionUi) return uiSchema;
  if (keyRef.current === optionKey) return mergedRef.current;
  const merged = { ...uiSchema, [keyOf]: optionUi };
  mergedRef.current = merged;
  keyRef.current = optionKey;
  return merged;
}

type OptionalUnionFieldContentProps<T, S extends StrictRJSFSchema, F extends FormContextType> = FieldProps<T, S, F> & {
  keyOf: "oneOf" | "anyOf";
  InnerField: ComponentType<FieldProps<T, S, F>>;
};

function OptionalUnionFieldContent<T = unknown, S extends StrictRJSFSchema = RJSFSchema, F extends FormContextType = Record<string, unknown>>(
  props: OptionalUnionFieldContentProps<T, S, F>
) {
  const { schema, formData, onChange, registry, uiSchema = {}, keyOf, InnerField } = props;
  const schemaObj = schema as Record<string, unknown>;
  const { schemaUtils } = registry;
  const config = useMemo(
    () => getOptionalUnionValueOption<T>(schemaObj, keyOf, (s, fd) => schemaUtils.retrieveSchema(s as S, fd)),
    [schemaObj, keyOf, schemaUtils]
  );
  const mergedUiSchema = useStableMergedUiSchema(uiSchema as Record<string, unknown>, schemaObj, keyOf);
  const valueSchema = config?.valueSchema;

  const wrappedOnChange = useCallback(
    (newValue: T | undefined, path: FieldPathList, es?: ErrorSchema<T>, id?: string) => {
      const normalized =
        valueSchema && isEmptyValue(valueSchema as Record<string, unknown>, newValue) ? (null as T) : newValue;
      onChange(normalized, path, es, id);
    },
    [onChange, valueSchema]
  );

  const innerUiSchema = useMemo(() => {
    const current = (uiSchema ?? {}) as Record<string, unknown>;
    const options = (current["ui:options"] as Record<string, unknown>) ?? {};
    return {
      ...current,
      "ui:options": { ...options, label: false },
    };
  }, [uiSchema]);

  if (!config) {
    return <InnerField {...(props as FieldProps<T, S, F>)} uiSchema={mergedUiSchema} />;
  }

  const SchemaField = registry.fields.SchemaField;
  return (
    <SchemaField
      {...(props as FieldProps<T, S, F>)}
      schema={valueSchema as unknown as S}
      uiSchema={innerUiSchema}
      onChange={wrappedOnChange}
      formData={formData === null || formData === undefined ? undefined : formData}
      required={false}
    />
  );
}

export function WrappedAnyOfField<T = unknown, S extends StrictRJSFSchema = RJSFSchema, F extends FormContextType = Record<string, unknown>>(
  props: FieldProps<T, S, F>
) {
  return (
    <OptionalUnionFieldContent
      {...(props as OptionalUnionFieldContentProps<T, S, F>)}
      keyOf={ANY_OF_KEY}
      InnerField={DefaultAnyOfField as unknown as ComponentType<FieldProps<T, S, F>>}
    />
  );
}

export function WrappedOneOfField<T = unknown, S extends StrictRJSFSchema = RJSFSchema, F extends FormContextType = Record<string, unknown>>(
  props: FieldProps<T, S, F>
) {
  return (
    <OptionalUnionFieldContent
      {...(props as OptionalUnionFieldContentProps<T, S, F>)}
      keyOf={ONE_OF_KEY}
      InnerField={DefaultOneOfField as unknown as ComponentType<FieldProps<T, S, F>>}
    />
  );
}
