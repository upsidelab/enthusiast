import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { TypeInfo } from "@/lib/types";
import { JSONEditor } from "./json-editor";
import { ListInput } from "./list-input";

interface DynamicConfigInputProps {
  id: string;
  label: string;
  value: string | number | boolean;
  onChange: (value: string | number | boolean) => void;
  typeInfo?: TypeInfo;
  description?: string;
  error?: string;
}

export function DynamicConfigInput({
  id,
  label,
  value,
  onChange,
  typeInfo,
  description,
  error
}: DynamicConfigInputProps) {
  const getInputType = () => {
    if (!typeInfo) return 'text';
    if (typeInfo.inner_type === 'Json') {
      return 'json';
    }
    if (typeInfo.container === 'list') {
      return 'list';
    }
    
    const baseType = typeInfo.inner_type || typeInfo.container;
    
    switch (baseType) {
      case 'int':
      case 'integer':
        return 'number';
      case 'float':
      case 'double':
        return 'number';
      case 'bool':
      case 'boolean':
        return 'boolean';
      case 'str':
      case 'string':
      default:
        return 'text';
    }
  };

  const getPlaceholder = () => {
    if (!typeInfo) return undefined;
    if (typeInfo.inner_type === 'Json') {
      return '{}';
    }
    
    const baseType = typeInfo.inner_type || typeInfo.container;
    
    switch (baseType) {
      case 'int':
      case 'integer':
        return '0';
      case 'float':
      case 'double':
        return '0.00';
      case 'str':
      case 'string':
      default:
        return undefined;
    }
  };

  const handleInputChange = (inputValue: string | boolean) => {
    const inputType = getInputType();
    
    if (inputType === 'boolean') {
      onChange(inputValue as boolean);
    } else if (inputType === 'number') {
      const numValue = inputValue === '' ? '' : Number(inputValue);
      onChange(numValue === '' ? '' : numValue);
    } else {
      onChange(inputValue as string);
    }
  };

  const handleJSONChange = (jsonString: string) => {
    onChange(jsonString);
  };

  const renderInput = () => {
    const inputType = getInputType();
    
    if (inputType === 'json') {
      return (
        <JSONEditor
          value={typeof value === 'string' ? value : '{}'}
          onChange={handleJSONChange}
          label={label}
          description={description}
          error={error}
        />
      );
    }
    
    if (inputType === 'list') {
      return (
        <ListInput
          id={id}
          label={label}
          value={typeof value === 'string' ? value : '[]'}
          onChange={onChange}
          description={description}
          error={error}
          innerType={typeInfo?.inner_type}
        />
      );
    }
    
    if (inputType === 'boolean') {
      return (
        <div className="flex items-center space-x-2">
          <Switch
            id={id}
            checked={value === true || value === 'true'}
            onCheckedChange={handleInputChange}
          />
          <Label htmlFor={id} className="text-sm">
            {value === true || value === 'true' ? 'Enabled' : 'Disabled'}
          </Label>
        </div>
      );
    }
    
    return (
      <Input
        id={id}
        type={inputType === 'number' ? 'number' : 'text'}
        placeholder={getPlaceholder()}
        value={value === '' ? '' : String(value)}
        onChange={(e) => handleInputChange(e.target.value)}
        className={`w-full ${error ? "border-destructive" : ""}`}
      />
    );
  };

  const inputType = getInputType();

  if (inputType === 'json' || inputType === 'list') {
    return renderInput();
  }

  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="text-sm font-medium">
        {label}
      </Label>
      {renderInput()}
      {description && (
        <p className="text-xs text-muted-foreground mb-2">{description}</p>
      )}
      {error && (
        <p className="text-xs text-destructive mb-3">{error}</p>
      )}
    </div>
  );
}
