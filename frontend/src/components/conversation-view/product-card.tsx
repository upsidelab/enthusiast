import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface ProductCardProps {
  id: number;
  name: string;
  sku: string;
  slug: string;
  description: string;
  categories: string;
  properties: string;
  price?: number;
}

export function ProductCard({ 
  name, 
  sku, 
  description, 
  categories, 
  properties,
  price
}: ProductCardProps) {
  let parsedCategories: string[] = [];
  if (categories) {
    try {
      const parsed = JSON.parse(categories);
      parsedCategories = Array.isArray(parsed) ? parsed : [String(parsed)];
    } catch {
      parsedCategories = categories.split(',').map(c => c.trim()).filter(Boolean);
    }
  }

  let parsedProperties: Record<string, string> = {};
  if (properties) {
    try {
      const parsed = JSON.parse(properties);
      if (typeof parsed === 'object' && parsed !== null) {
        parsedProperties = parsed;
      }
    } catch {
      properties.split(';').forEach(pair => {
        const [key, value] = pair.split('->').map(s => s.trim());
        if (key && value) {
          parsedProperties[key] = value;
        }
      });
    }
  }

  return (
    <Card className="transition-all hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-baseline gap-2 mb-0.5">
          <CardTitle className="text-base truncate">{name}</CardTitle>
          {price !== undefined && (
            <span className="text-base font-bold text-primary whitespace-nowrap">
              ${price.toFixed(2)}
            </span>
          )}
        </div>
        <CardDescription className="text-xs">
          SKU: {sku}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-0 pb-4">
        {description && (
          <p className="text-xs text-gray-600 mb-2 line-clamp-2">
            {description}
          </p>
        )}
        
        {parsedCategories.length > 0 && (
          <div className="mb-2">
            <div className="flex flex-wrap gap-1">
              {parsedCategories.slice(0, 3).map((category: string, index: number) => (
                <Badge key={index} variant="secondary" className="text-[10px] px-1.5 py-0">
                  {category}
                </Badge>
              ))}
              {parsedCategories.length > 3 && (
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                  +{parsedCategories.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {Object.keys(parsedProperties).length > 0 && (
          <div className="text-[11px] text-gray-500 space-y-0.5">
            {Object.entries(parsedProperties).slice(0, 3).map(([key, value], index) => (
              <div key={index} className="flex justify-between gap-2">
                <span className="font-medium">{key}:</span>
                <span className="truncate">{String(value)}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

