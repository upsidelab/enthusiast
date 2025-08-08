import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { TypeInfo } from "@/lib/types";

interface DynamicConfigInputProps {
  id: string;
  label: string;
  placeholder?: string;
  value: string | number | boolean;
  onChange: (value: string | number | boolean) => void;
  typeInfo?: TypeInfo;
  description?: string;
  error?: string;
}

export function DynamicConfigInput({
  id,
  label,
  placeholder,
  value,
  onChange,
  typeInfo,
  description,
  error
}: DynamicConfigInputProps) {
  const getInputType = () => {
    if (!typeInfo) return 'text';
    
    if (typeInfo.container === 'list') {
      return 'text'; // For now, handle lists as text input
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

  const renderInput = () => {
    const inputType = getInputType();
    
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
        placeholder={placeholder}
        value={value === '' ? '' : String(value)}
        onChange={(e) => handleInputChange(e.target.value)}
        className={`w-full ${error ? "border-destructive" : ""}`}
      />
    );
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="text-sm font-medium">
        {label}
      </Label>
      {renderInput()}
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
      {error && (
        <p className="text-xs text-destructive">{error}</p>
      )}
    </div>
  );
}
