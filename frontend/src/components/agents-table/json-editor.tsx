import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

interface JSONEditorProps {
  value: string | Record<string, unknown>;
  onChange: (value: string) => void;
  label: string;
  description?: string;
  error?: string;
}

export const JSONEditor: React.FC<JSONEditorProps> = ({
  value,
  onChange,
  label,
  description,
  error
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [jsonString, setJsonString] = useState(() => {
    if (typeof value === 'string') {
      return value.trim() || '{}';
    }
    if (typeof value === 'object' && value !== null) {
      try {
        return JSON.stringify(value, null, 2);
      } catch {
        return '{}';
      }
    }
    return '{}';
  });
  const [jsonError, setJsonError] = useState<string | null>(null);

  useEffect(() => {
    const stringValue = valueToString(value);
    if (stringValue !== jsonString) {
      try {
        JSON.parse(stringValue);
        setJsonString(stringValue);
        setJsonError(null);
      } catch {
        setJsonError('Invalid JSON format');
        setJsonString(stringValue);
      }
    }
  }, [value]);

  const handleOpenModal = () => {
    const stringValue = valueToString(value);
    setJsonString(stringValue);
    setJsonError(null);
    setIsModalOpen(true);
  };

  const handleJsonChange = (newJsonString: string) => {
    setJsonString(newJsonString);
    try {
      JSON.parse(newJsonString);
      setJsonError(null);
    } catch {
      setJsonError('Invalid JSON format');
    }
  };

  const handleSave = () => {
    if (!jsonError) {
      onChange(jsonString);
      setIsModalOpen(false);
    }
  };

  const handleCancel = () => {
    const resetValue = valueToString(value);
    setJsonString(resetValue);
    try {
      JSON.parse(resetValue);
      setJsonError(null);
    } catch {
      setJsonError('Invalid JSON format');
    }
    setIsModalOpen(false);
  };

  const valueToString = (val: string | Record<string, unknown>): string => {
    if (typeof val === 'string') {
      return val;
    }
    if (typeof val === 'object' && val !== null) {
      try {
        return JSON.stringify(val, null, 2);
      } catch {
        return '{}';
      }
    }
    return '{}';
  };

  const getDisplayValue = (val: string | Record<string, unknown>): string => {
    if (!val || (typeof val === 'string' && val.trim() === '')) {
      return '{}';
    }
    
    const strValue = valueToString(val);
    try {
      const parsed = JSON.parse(strValue);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return strValue || '{}';
    }
  };

  return (
    <>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">
            {label}
          </Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleOpenModal}
          >
            Edit JSON
          </Button>
        </div>
        
        <div className="p-3 bg-muted rounded-md border">
          <pre className="text-xs overflow-auto max-h-32 font-mono">
            {getDisplayValue(value)}
          </pre>
        </div>
        
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
        
        {error && (
          <p className="text-xs text-destructive">{error}</p>
        )}
      </div>
      
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-4xl" noBackdrop>
          <DialogHeader>
            <DialogTitle>Edit JSON - {label}</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="json_data">JSON Data</Label>
              <div className="border rounded-md">
                <Textarea
                  id="json_data"
                  placeholder='{"key": "value", "nested": {"option": true}}'
                  value={jsonString}
                  onChange={(e) => handleJsonChange(e.target.value)}
                  rows={15}
                  className="font-mono text-sm resize-none overflow-auto max-h-96"
                  style={{ minHeight: '300px' }}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Enter valid JSON data
              </p>
            </div>

            {jsonError && (
              <Alert variant="destructive">
                <AlertDescription>{jsonError}</AlertDescription>
              </Alert>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={!!jsonError}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
