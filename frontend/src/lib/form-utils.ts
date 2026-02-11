/**
 * Common form utilities for configuration handling
 */

export function flattenConfigForForm(
  config: unknown, 
  sectionMapping?: Record<string, string>
): Record<string, string | number | boolean> {
  const flattenedConfig: Record<string, string | number | boolean> = {};
  
  if (!config || typeof config !== 'object') {
    return flattenedConfig;
  }
  
  Object.entries(config as Record<string, unknown>).forEach(([section, sectionData]) => {
    const frontendSection = sectionMapping?.[section] || section;
    
    if (Array.isArray(sectionData)) {
      sectionData.forEach(obj => {
        if (obj && typeof obj === 'object') {
          Object.entries(obj).forEach(([key, value]) => {
            if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
              flattenedConfig[`${frontendSection}_${key}`] = value;
            } else if (typeof value === 'object' && value !== null) {
              try {
                flattenedConfig[`${frontendSection}_${key}`] = JSON.stringify(value);
              } catch {
                flattenedConfig[`${frontendSection}_${key}`] = '{}';
              }
            }
          });
        }
      });
    } else if (sectionData && typeof sectionData === 'object') {
      Object.entries(sectionData).forEach(([key, value]) => {
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
          flattenedConfig[`${frontendSection}_${key}`] = value;
        } else if (typeof value === 'object' && value !== null) {
          try {
            flattenedConfig[`${frontendSection}_${key}`] = JSON.stringify(value);
          } catch {
            flattenedConfig[`${frontendSection}_${key}`] = '{}';
          }
        }
      });
    }
  });
  
  return flattenedConfig;
}

export function buildConfigFromFlattened(
  config: Record<string, string | number | boolean>,
  sectionMapping?: Record<string, string>
): Record<string, unknown> {
  const configObj: Record<string, unknown> = {};
  const sections: Record<string, Record<string, unknown>> = {};
  
  Object.entries(config).forEach(([key, value]) => {
    if (key.includes('_')) {
      const firstUnderscoreIndex = key.indexOf('_');
      const section = key.substring(0, firstUnderscoreIndex);
      const fieldName = key.substring(firstUnderscoreIndex + 1);
      
      if (!sections[section]) {
        sections[section] = {};
      }
      
      if (typeof value === 'string' && value.trim() !== '') {
        try {
          const parsedValue = JSON.parse(value);
          sections[section][fieldName] = parsedValue;
        } catch {
          sections[section][fieldName] = value;
        }
      } else if (typeof value === 'number' || typeof value === 'boolean') {
        sections[section][fieldName] = value;
      }
    }
  });
  
  Object.entries(sections).forEach(([section, fields]) => {
    if (Object.keys(fields).length > 0) {
      const sectionKey = sectionMapping?.[section] || section;
      configObj[sectionKey] = fields;
    }
  });

  if (Object.keys(configObj).length === 0 && sectionMapping) {
    Object.values(sectionMapping).forEach(sectionKey => {
      configObj[sectionKey] = {};
    });
  }
  
  return configObj;
}

export function parseFieldErrors(errorData: unknown): Record<string, string> {
  const newFieldErrors: Record<string, string> = {};
  
  if (!(typeof errorData === 'object') || !errorData) {
    return newFieldErrors;
  }

  // Handle basic field errors (Django may return array e.g. ["error"] or string "error")
  const skipKeys = ['config', 'detail', 'message'];
  Object.entries(errorData as Record<string, unknown>).forEach(([key, value]) => {
    if (skipKeys.includes(key)) return;
    if (Array.isArray(value) && value.length > 0) {
      newFieldErrors[key] = String(value[0]);
    } else if (typeof value === 'string') {
      newFieldErrors[key] = value;
    }
  });

  // Handle nested config errors
  if ('config' in errorData && typeof errorData.config === 'object' && errorData.config) {
    Object.entries(errorData.config as Record<string, unknown>).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        newFieldErrors[`configuration_${key}`] = String(value[0]);
      }
    });
  }

  return newFieldErrors;
}
