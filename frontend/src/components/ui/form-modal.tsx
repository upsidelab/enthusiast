import { useRef, useEffect, useState, ReactNode } from "react";
import { ConfigurationModal } from "@/components/ui/configuration-modal";

interface FormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  onSubmit: () => void;
  onCancel: () => void;
  submitLabel: string;
  submitting: boolean;
  disabled?: boolean;
  loading?: boolean;
  loadingText?: string;
  children: ReactNode;
  dependencies?: any[]; // For scroll effect dependencies
}

export function FormModal({
  open,
  onOpenChange,
  title,
  onSubmit,
  onCancel,
  submitLabel,
  submitting,
  disabled = false,
  loading = false,
  loadingText = "Loading...",
  children,
  dependencies = []
}: FormModalProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showFade, setShowFade] = useState(false);

  useEffect(() => {
    const checkIfScrollingNeeded = () => {
      if (scrollContainerRef.current) {
        const { scrollHeight, clientHeight } = scrollContainerRef.current;
        const hasOverflow = scrollHeight > clientHeight;
        setShowFade(hasOverflow);
      }
    };

    const setupScrollObserver = () => {
      const resizeObserver = new ResizeObserver(checkIfScrollingNeeded);
      if (scrollContainerRef.current) {
        resizeObserver.observe(scrollContainerRef.current);
      }
      return resizeObserver;
    };

    const cleanupScrollObserver = (observer: ResizeObserver) => {
      observer.disconnect();
    };

    checkIfScrollingNeeded();
    const observer = setupScrollObserver();
    return () => cleanupScrollObserver(observer);
  }, dependencies);

  return (
    <ConfigurationModal
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      onSubmit={onSubmit}
      onCancel={onCancel}
      submitLabel={submitLabel}
      submitting={submitting}
      disabled={disabled}
      loading={loading}
      loadingText={loadingText}
    >
      <div className="relative">
        <div 
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto space-y-4 px-2 [&::-webkit-scrollbar]:hidden max-h-[60vh]"
          style={{
            scrollbarWidth: 'none',
            msOverflowStyle: 'none'
          }}
        >
          {children}
        </div>
        {showFade && (
          <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-background to-transparent pointer-events-none"></div>
        )}
      </div>
    </ConfigurationModal>
  );
}
