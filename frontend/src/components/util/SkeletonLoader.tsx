import { ReactNode, useEffect, useState } from "react";

export interface SkeletonLoaderProps {
  children: ReactNode[];
  skeleton: ReactNode;
  isLoading: boolean;
}

export function SkeletonLoader({ children, skeleton, isLoading }: SkeletonLoaderProps) {
  const [shouldShowSkeleton, setShouldShowSkeleton] = useState(true);

  useEffect(() => {
    setTimeout(() => setShouldShowSkeleton(false), 200);
  }, []);

  return (isLoading || shouldShowSkeleton) ? skeleton : children;
}
