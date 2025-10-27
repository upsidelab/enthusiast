import { TypeInfo } from "@/lib/types";

export function parseListValue(value: string | number | boolean, innerType?: string): unknown {
  if (typeof value !== 'string') return value;
  
  try {
    const parsed = JSON.parse(value);
    if (!Array.isArray(parsed)) return value;
    
    if (innerType === 'int' || innerType === 'integer') {
      return parsed.map(item => parseInt(String(item), 10));
    } else if (innerType === 'float' || innerType === 'double') {
      return parsed.map(item => parseFloat(String(item)));
    } else {
      return parsed.map(String);
    }
  } catch {
    return value;
  }
}

export function buildConfigValue(
  value: string | number | boolean,
  typeInfo?: { container?: string; inner_type?: string }
): unknown {
  if (typeInfo?.container === 'list') {
    return parseListValue(value, typeInfo.inner_type);
  } else if (typeof value === 'string' && value.trim() !== '') {
    try {
      const parsedValue = JSON.parse(value);
      return parsedValue;
    } catch {
      return value;
    }
  } else {
    return value;
  }
}

export function parseNestedConfigErrors(
  errorData: unknown,
  errorKey: string,
  fieldPrefix: string
): Record<string, string> {
  const newFieldErrors: Record<string, string> = {};
  
  if (typeof errorData === 'object' && errorData && errorKey in errorData) {
    const configErrors = (errorData as Record<string, unknown>)[errorKey];
    if (typeof configErrors === 'object' && configErrors) {
      Object.entries(configErrors as Record<string, unknown>).forEach(([field, error]) => {
        const fieldName = field.split('.')[0];
        const errorMessage = Array.isArray(error) ? String(error[0]) : String(error);
        newFieldErrors[`${fieldPrefix}_${fieldName}`] = errorMessage;
      });
    }
  }
  
  return newFieldErrors;
}

export function buildConfigFromFlatForm(
  config: Record<string, string | number | boolean>,
  configSections: Record<string, Record<string, unknown> | Record<string, unknown>[]>,
  prefix: string
): Record<string, unknown> {
  const configObj: Record<string, unknown> = {};
  
  Object.entries(configSections).forEach(([section, fields]) => {
    if (Array.isArray(fields)) {
      configObj[section] = fields.map(obj => {
        if (!obj || typeof obj !== 'object') return {};
        
        const out: Record<string, unknown> = {};
        Object.entries(obj).forEach(([k, schema]) => {
          const configKey = `${prefix}${section}_${k}`;
          const v = config[configKey];
          if (v !== '' && v !== null && v !== undefined) {
            const schemaObj = schema as Record<string, unknown>;
            const typeInfo = schemaObj?.type as { container?: string; inner_type?: string } | undefined;
            out[k] = buildConfigValue(v, typeInfo);
          }
        });
        return out;
      });
    } else if (fields && typeof fields === 'object') {
      const sectionObj: Record<string, unknown> = {};
      Object.entries(fields).forEach(([k, schema]) => {
        const configKey = `${prefix}${section}_${k}`;
        const v = config[configKey];
        if (v !== '' && v !== null && v !== undefined) {
          const schemaObj = schema as Record<string, unknown>;
          const typeInfo = schemaObj?.type as { container?: string; inner_type?: string } | undefined;
          sectionObj[k] = buildConfigValue(v, typeInfo);
        }
      });
      configObj[section] = sectionObj;
    }
  });
  
  return configObj;
}

export function buildSinglePrefixConfig(
  config: Record<string, string | number | boolean>,
  schemas: Record<string, { type: TypeInfo }>,
  prefix: string
): Record<string, unknown> {
  const configObj: Record<string, unknown> = {};
  
  Object.entries(config).forEach(([key, value]) => {
    if (key.startsWith(prefix)) {
      const fieldName = key.substring(prefix.length);
      
      if (value !== '' && value !== null && value !== undefined) {
        const schema = schemas[fieldName];
        const typeInfo = schema?.type;
        const typeInfoObj = typeInfo ? {
          container: typeInfo.container || undefined,
          inner_type: typeInfo.inner_type || undefined
        } : undefined;
        
        if (typeInfoObj?.container === 'list') {
          configObj[fieldName] = parseListValue(value, typeInfoObj.inner_type);
        } else {
          configObj[fieldName] = buildConfigValue(value, typeInfoObj);
        }
      }
    }
  });
  
  return configObj;
}

