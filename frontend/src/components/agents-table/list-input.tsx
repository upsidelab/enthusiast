import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Trash2 } from "lucide-react";

interface ListInputProps {
  id: string;
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  description?: string;
  error?: string;
  innerType?: string;
}

export function ListInput({
  id,
  label,
  placeholder,
  value,
  onChange,
  description,
  error,
  innerType
}: ListInputProps) {
  const getInputType = () => {
    if (!innerType) return 'text';
    switch (innerType) {
      case 'int':
      case 'integer':
        return 'number';
      case 'float':
      case 'double':
        return 'number';
      case 'str':
      case 'string':
      default:
        return 'text';
    }
  };

  const isIntegerType = () => {
    return innerType === 'int' || innerType === 'integer';
  };

  const [items, setItems] = useState<string[]>(() => {
    if (!value) return [''];
    try {
      const parsed = JSON.parse(value);
      return Array.isArray(parsed) ? parsed.map(String) : [''];
    } catch {
      return [''];
    }
  });

  const [itemErrors, setItemErrors] = useState<Record<number, string>>({});

  const inputType = getInputType();

  const handleItemChange = (index: number, newValue: string) => {
    const newItems = [...items];
    const newErrors = { ...itemErrors };
    
    if (isIntegerType()) {
      if (newValue.includes('.') || newValue.includes(',')) {
        newErrors[index] = "Only whole numbers (integers) are allowed";
        newItems[index] = newValue;
      } else {
        newItems[index] = newValue;
        delete newErrors[index];
      }
    } else {
      delete newErrors[index];
      newItems[index] = newValue;
    }
    
    setItemErrors(newErrors);
    setItems(newItems);
    onChange(JSON.stringify(newItems));
  };

  const handleAddItem = () => {
    setItems([...items, '']);
    onChange(JSON.stringify([...items, '']));
  };

  const handleRemoveItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    const newErrors: Record<number, string> = {};
    
    newItems.forEach((_, i) => {
      const originalIndex = items.findIndex((_, origIndex) => origIndex === i);
      if (itemErrors[originalIndex]) {
        newErrors[i] = itemErrors[originalIndex];
      }
    });
    
    setItemErrors(newErrors);
    
    if (newItems.length === 0) {
      setItems(['']);
      onChange(JSON.stringify(['']));
    } else {
      setItems(newItems);
      onChange(JSON.stringify(newItems));
    }
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="text-sm font-medium">
        {label}
      </Label>
      
      <div className="space-y-2">
        {items.map((item, index) => {
          const hasItemError = itemErrors[index];
          const hasGlobalError = error;
          return (
            <div key={index} className="space-y-1 mb-3">
              <div className="flex items-center gap-2">
                <Input
                  id={`${id}-${index}`}
                  type={inputType}
                  placeholder={placeholder || (isIntegerType() ? "0" : inputType === 'number' ? "0.00" : undefined)}
                  value={item}
                  onChange={(e) => handleItemChange(index, e.target.value)}
                  onKeyDown={(e) => {
                    if (isIntegerType()) {
                      if (e.key === '.' || e.key === ',' || e.key === 'e' || e.key === 'E') {
                        e.preventDefault();
                        const newErrors = { ...itemErrors };
                        newErrors[index] = "Only whole numbers (integers) are allowed";
                        setItemErrors(newErrors);
                      }
                    }
                  }}
                  className={`flex-1 ${hasItemError || hasGlobalError ? "border-destructive" : ""}`}
                  step={isIntegerType() ? "1" : inputType === 'number' ? "any" : undefined}
                  min={inputType === 'number' ? undefined : undefined}
                />
                {items.length > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => handleRemoveItem(index)}
                    aria-label="Remove item"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
              {itemErrors[index] && (
                <p className="text-xs text-destructive ml-0.5">{itemErrors[index]}</p>
              )}
            </div>
          );
        })}
        
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAddItem}
          className="w-full"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Item
        </Button>
      </div>
      
      {description && (
        <p className="text-xs text-muted-foreground mb-2">{description}</p>
      )}
      {error && (
        <p className="text-xs text-destructive mt-1 mb-4">{error}</p>
      )}
    </div>
  );
}
