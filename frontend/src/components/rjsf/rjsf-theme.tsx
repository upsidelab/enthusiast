/* eslint-disable react-refresh/only-export-components -- theme file exports widgets, templates and rjsfWidgets/rjsfTemplates */
import { useCallback, useMemo } from "react";
import type {
  ArrayFieldItemButtonsTemplateProps,
  ArrayFieldItemTemplateProps,
  ArrayFieldTemplateProps,
  BaseInputTemplateProps,
  DescriptionFieldProps,
  FieldErrorProps,
  FieldTemplateProps,
  FormContextType,
  MultiSchemaFieldTemplateProps,
  RJSFSchema,
  StrictRJSFSchema,
  WidgetProps,
} from "@rjsf/utils";
import {
  enumOptionsIndexForValue,
  enumOptionsValueForIndex,
  getDiscriminatorFieldFromSchema,
  getTemplate,
  getUiOptions,
} from "@rjsf/utils";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { JsonEditorWidget } from "./rjsf-json-editor-widget";
import { isOptionalUnionSchema } from "./rjsf-multischema-field-template";
import { getInputProps } from "@rjsf/utils";
import { Plus, Trash2, ChevronUp, ChevronDown, Copy } from "lucide-react";

function FieldTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: FieldTemplateProps<T, S, F>) {
  const {
    id,
    label,
    children,
    errors,
    help,
    description,
    hidden,
    required,
    displayLabel,
    uiSchema,
    schema,
    registry,
    rawErrors,
  } = props;
  const uiOptions = getUiOptions(uiSchema);
  const isCheckbox = uiOptions.widget === "checkbox";
  const isJsonWidget = uiOptions.widget === "json";
  const hasError = Boolean(rawErrors?.length);
  const titleOrKey = (schema as { title?: string })?.title ?? label ?? "";
  const optionalUnion =
    schema &&
    typeof schema === "object" &&
    (("oneOf" in (schema as object)) || ("anyOf" in (schema as object))) &&
    isOptionalUnionSchema(schema as Record<string, unknown>, (s, fd) =>
      registry.schemaUtils.retrieveSchema(s as S, fd as T | undefined)
    );
  const showRequired =
    required &&
    !optionalUnion &&
    (schema as { default?: unknown }).default === undefined;

  if (hidden) {
    return <div className="hidden">{children}</div>;
  }

  const showFieldTemplateLabel = displayLabel && !isCheckbox && titleOrKey && !isJsonWidget;

  return (
    <div
      className="flex flex-col gap-1"
      {...(hasError ? { "data-field-error": "true" } : {})}
    >
      {showFieldTemplateLabel && (
        <Label htmlFor={id} className="text-sm font-medium">
          {titleOrKey}
          {showRequired && <span className="text-destructive ml-0.5">*</span>}
        </Label>
      )}
      {children}
      {displayLabel && description ? description : null}
      {hasError && (errors ?? (rawErrors?.length ? (
        rawErrors.filter(Boolean).map((e, i) => (
          <p key={i} className="text-xs text-destructive">{e}</p>
        ))
      ) : null))}
      {help}
    </div>
  );
}

function BaseInputTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: BaseInputTemplateProps<T, S, F>) {
  const {
    id,
    value,
    readonly,
    disabled,
    autofocus,
    onBlur,
    onFocus,
    onChange,
    schema,
    rawErrors,
    type,
  } = props;
  const inputProps = getInputProps<T, S, F>(schema, type, props.options);
  const inputType =
    type === "integer" || type === "number"
      ? "number"
      : (inputProps.type as "text" | "number") ?? "text";
  const inputValue =
    type === "number" || type === "integer"
      ? value || value === 0
        ? value
        : ""
      : value == null
        ? ""
        : value;

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const v = e.target.value;
      onChange(v === "" ? null : v);
    },
    [onChange]
  );

  return (
    <Input
      id={id}
      type={inputType}
      value={inputValue}
      readOnly={readonly}
      disabled={disabled}
      autoFocus={autofocus}
      onBlur={(e) => onBlur(id, (e.target as HTMLInputElement).value)}
      onFocus={(e) => onFocus(id, (e.target as HTMLInputElement).value)}
      onChange={handleChange}
      className={rawErrors?.length ? "border-destructive" : ""}
    />
  );
}

function FieldErrorTemplate(props: FieldErrorProps) {
  const { errors = [] } = props;
  if (errors.length === 0) return null;
  return (
    <>
      {errors.filter(Boolean).map((error, i) => (
        <p key={i} className="text-xs text-destructive">
          {error}
        </p>
      ))}
    </>
  );
}

function DescriptionFieldTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: DescriptionFieldProps<T, S, F>) {
  const { id, description } = props;
  if (!description) return null;
  return (
    <div id={id} className="text-xs text-muted-foreground mt-1 field-description">
      {description}
    </div>
  );
}

function ArrayFieldTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: ArrayFieldTemplateProps<T, S, F>) {
  const { title, required, items, onAddClick, disabled, readonly, registry } = props;
  const formContext = registry.formContext as { toolsFormData?: unknown } | undefined;
  const isToolsSection = Boolean(formContext?.toolsFormData);
  const showAddButton = !isToolsSection && !readonly && !disabled;

  return (
    <div className="space-y-2">
      {title && (
        <Label className="text-sm font-medium">
          {title}
          {required && <span className="text-destructive ml-0.5">*</span>}
        </Label>
      )}
      <div className="space-y-3 mt-2 array-item-list">
        {items.map((item) => (
          <div key={item.key}>{item}</div>
        ))}
      </div>
      {showAddButton && (
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-2 rjsf-array-item-add"
          onClick={onAddClick}
        >
          <Plus className="h-4 w-4 mr-1" />
          Add
        </Button>
      )}
    </div>
  );
}

function ArrayFieldItemTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: ArrayFieldItemTemplateProps<T, S, F>) {
  const { children, buttonsProps, hasToolbar, index, registry } = props;
  const formContext = registry.formContext as { toolsFormData?: Record<string, unknown>[] } | undefined;
  const toolsFormData = formContext?.toolsFormData;
  const itemData = toolsFormData?.[index];
  const isEmptyToolConfig =
    toolsFormData &&
    itemData !== undefined &&
    typeof itemData === "object" &&
    itemData !== null &&
    Object.keys(itemData).length === 0;
  if (isEmptyToolConfig) {
    return null;
  }

  const ArrayFieldItemButtonsTemplate = getTemplate<"ArrayFieldItemButtonsTemplate", T, S, F>(
    "ArrayFieldItemButtonsTemplate",
    props.registry,
    props.registry.globalUiOptions
  );

  return (
    <div className="flex items-start gap-2 rounded-md border border-border bg-muted/20 p-3 rjsf-array-item">
      <div className="flex-1 min-w-0">{children}</div>
      {hasToolbar && (
        <div className="flex shrink-0 gap-1 array-item-toolbox">
          <ArrayFieldItemButtonsTemplate {...buttonsProps} />
        </div>
      )}
    </div>
  );
}

function ArrayFieldItemButtonsTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: ArrayFieldItemButtonsTemplateProps<T, S, F>) {
  const { disabled, hasCopy, hasMoveDown, hasMoveUp, hasRemove, onCopyItem, onMoveDownItem, onMoveUpItem, onRemoveItem, readonly } = props;

  return (
    <>
      {hasMoveUp && (
        <Button type="button" variant="ghost" size="icon" onClick={onMoveUpItem} disabled={disabled || readonly}>
          <ChevronUp className="h-4 w-4" />
        </Button>
      )}
      {hasMoveDown && (
        <Button type="button" variant="ghost" size="icon" onClick={onMoveDownItem} disabled={disabled || readonly}>
          <ChevronDown className="h-4 w-4" />
        </Button>
      )}
      {hasCopy && (
        <Button type="button" variant="ghost" size="icon" onClick={onCopyItem} disabled={disabled || readonly}>
          <Copy className="h-4 w-4" />
        </Button>
      )}
      {hasRemove && (
        <Button type="button" variant="ghost" size="icon" onClick={onRemoveItem} disabled={disabled || readonly}>
          <Trash2 className="h-4 w-4" />
        </Button>
      )}
    </>
  );
}

function MultiSchemaFieldTemplate<
  T = unknown,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = Record<string, unknown>,
>(props: MultiSchemaFieldTemplateProps<T, S, F>) {
  const { selector, optionSchemaField } = props;
  return (
    <div className="space-y-1 rounded-md border border-border bg-muted/20 p-1">
      {selector && <div className="space-y-2">{selector}</div>}
      {optionSchemaField && (
        <div className="pt-1 border-t border-border/50">{optionSchemaField}</div>
      )}
    </div>
  );
}

function TextareaWidget<T = unknown, S extends StrictRJSFSchema = RJSFSchema, F extends FormContextType = Record<string, unknown>>(
  props: WidgetProps<T, S, F>
) {
  const { id, value, readonly, disabled, onChange, onBlur, onFocus, rawErrors } = props;
  return (
    <Textarea
      id={id}
      value={value ?? ""}
      readOnly={readonly}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
      onBlur={(e) => onBlur(id, (e.target as HTMLTextAreaElement).value)}
      onFocus={(e) => onFocus(id, (e.target as HTMLTextAreaElement).value)}
      className={rawErrors?.length ? "border-destructive" : ""}
    />
  );
}

function CheckboxWidget<T = unknown, S extends StrictRJSFSchema = RJSFSchema, F extends FormContextType = Record<string, unknown>>(
  props: WidgetProps<T, S, F>
) {
  const { id, value, disabled, readonly, onChange, label } = props;
  return (
    <div className="flex items-center gap-2">
      <Switch
        id={id}
        checked={!!value}
        disabled={disabled || readonly}
        onCheckedChange={(checked) => onChange(checked)}
      />
      {label && <Label htmlFor={id} className="text-sm font-medium">{label}</Label>}
    </div>
  );
}

const SELECT_EMPTY_VALUE = "__rjsf_empty__";

function SelectWidget<T = unknown, S extends StrictRJSFSchema = RJSFSchema, F extends FormContextType = Record<string, unknown>>(
  props: WidgetProps<T, S, F>
) {
  const {
    schema,
    options = {},
    value,
    required,
    disabled,
    readonly,
    onChange,
    placeholder,
    rawErrors,
  } = props;
  const optsOptions = options as {
    enumOptions?: { value: unknown; label: string }[];
    emptyValue?: unknown;
    optionsSchemaSelector?: string;
  };
  const { enumOptions = [], emptyValue: optEmptyVal, optionsSchemaSelector } = optsOptions ?? {};
  const opts = useMemo(() => (Array.isArray(enumOptions) ? enumOptions : []), [enumOptions]);
  const multiple = false;

  const valueIsObject = typeof value === "object" && value !== null;
  const selectorField = optionsSchemaSelector ?? getDiscriminatorFieldFromSchema(schema as never);
  let valueForIndex: unknown = value;
  if (valueIsObject) {
    if (selectorField) {
      valueForIndex = (value as Record<string, unknown>)[selectorField];
    } else {
      const objValues = Object.values(value as object);
      const match = opts.find((o) => typeof o.value !== "object" && objValues.includes(o.value));
      valueForIndex = match?.value;
    }
  }

  const selectedIndexes = enumOptionsIndexForValue<S>(valueForIndex as never, opts as never, multiple);
  const selectedIndex =
    selectedIndexes === undefined
      ? undefined
      : Array.isArray(selectedIndexes)
        ? selectedIndexes[0]
        : selectedIndexes;
  const selectValue = selectedIndex !== undefined ? selectedIndex : SELECT_EMPTY_VALUE;
  const showPlaceholderOption = selectValue === SELECT_EMPTY_VALUE;

  const handleChange = useCallback(
    (val: string) => {
      if (val === SELECT_EMPTY_VALUE || val === "") {
        onChange((optEmptyVal ?? null) as T);
        return;
      }
      const actual = enumOptionsValueForIndex<S>(val as never, opts as never, optEmptyVal as never) as T;
      onChange(actual);
    },
    [onChange, opts, optEmptyVal]
  );

  return (
    <Select
      value={selectValue}
      onValueChange={handleChange}
      disabled={disabled || readonly}
      required={required}
    >
      <SelectTrigger className={rawErrors?.length ? "border-destructive" : ""}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {showPlaceholderOption && (
          <SelectItem value={SELECT_EMPTY_VALUE}>
            {placeholder ?? "Select…"}
          </SelectItem>
        )}
        {opts.map((opt: { value: unknown; label: string }, idx: number) => (
          <SelectItem key={idx} value={String(idx)}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export const rjsfTemplates = {
  FieldTemplate,
  BaseInputTemplate,
  FieldErrorTemplate,
  DescriptionFieldTemplate,
  ArrayFieldTemplate,
  ArrayFieldItemTemplate,
  ArrayFieldItemButtonsTemplate,
  MultiSchemaFieldTemplate,
};

export const rjsfWidgets = {
  TextareaWidget,
  CheckboxWidget,
  SelectWidget,
  json: JsonEditorWidget,
};
