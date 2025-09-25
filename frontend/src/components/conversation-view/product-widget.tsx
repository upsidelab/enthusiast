import { useState, useEffect } from 'react';
import { ProductCard, ProductCardProps } from './product-card';
import { BaseBubble } from './base-bubble';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export interface ProductWidgetProps {
  message?: string;
  products: ProductCardProps[];
  isStreaming?: boolean;
  expectedProductCount?: number;
}

function ProductPlaceholder() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm p-4 overflow-hidden relative">
      <div className="animate-pulse">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-3/4 mb-1 animate-shimmer"></div>
            <div className="h-3 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-1/4 animate-shimmer"></div>
          </div>
          <div className="h-7 w-7 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded animate-shimmer"></div>
        </div>
        <div className="space-y-1.5 mb-2">
          <div className="h-3 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-full animate-shimmer"></div>
          <div className="h-3 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-5/6 animate-shimmer"></div>
        </div>
        <div className="flex gap-1.5">
          <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-full w-16 animate-shimmer"></div>
          <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-full w-16 animate-shimmer"></div>
        </div>
      </div>
    </div>
  );
}

export function ProductWidget({ 
  message, 
  products, 
  isStreaming = false,
  expectedProductCount = 0
}: ProductWidgetProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState<string>("");
  const [shouldAnimate, setShouldAnimate] = useState(isStreaming);

  useEffect(() => {
    if (isStreaming) {
      setShouldAnimate(true);
    }
  }, [isStreaming]);

  useEffect(() => {
    if (message) {
      const processText = async () => {
        const renderer = new marked.Renderer();
        renderer.link = ({ href, title, tokens }) => {
          const text = tokens.map(token => token.raw).join('');
          const titleAttr = title ? ` title="${title}"` : '';
          return `<a href="${href}" target="_blank" rel="noopener noreferrer"${titleAttr}>${text}</a>`;
        };

        const rawHtml = await marked(message, { renderer });
        const cleanHtml = DOMPurify.sanitize(rawHtml);
        setSanitizedHtml(cleanHtml);
      };

      processText();
    }
  }, [message]);

  const totalSlots = expectedProductCount || products.length;
  const productsReceived = products.length;
  const productDelayMS = 500

  return (
    <BaseBubble variant="secondary" hasBackground={true}>
      {message && (
        <div className="mb-4 text-sm" dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
      )}
      
      <div className="space-y-2">
        {products.map((product, index) => (
          <div 
            key={product.id || `product-${index}`}
            className={shouldAnimate ? "grid" : ""}
          >
            {shouldAnimate ? (
              <>
                <div 
                  className="col-start-1 row-start-1 animate-fadeOut"
                  style={{ animationDelay: `${index * productDelayMS}ms` }}
                >
                  <ProductPlaceholder />
                </div>
                <div 
                  className="col-start-1 row-start-1 animate-fadeIn"
                  style={{ animationDelay: `${index * productDelayMS}ms` }}
                >
                  <ProductCard {...product} />
                </div>
              </>
            ) : (
              <ProductCard {...product} />
            )}
          </div>
        ))}
        
        {isStreaming && Array.from({ length: Math.max(0, totalSlots - productsReceived) }).map((_, index) => (
          <ProductPlaceholder key={`placeholder-${productsReceived + index}`} />
        ))}
      </div>
    </BaseBubble>
  );
}

