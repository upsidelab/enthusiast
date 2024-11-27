import * as React from "react";
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import { ButtonProps, buttonVariants } from "@/components/ui/button";

const Pagination = ({ className, ...props }: React.ComponentProps<"nav">) => (
  <nav
    role="navigation"
    aria-label="pagination"
    className={cn("mx-auto flex w-full justify-center", className)}
    {...props}
  />
);
Pagination.displayName = "Pagination";

const PaginationContent = React.forwardRef<
  HTMLUListElement,
  React.ComponentProps<"ul">
>(({ className, ...props }, ref) => (
  <ul
    ref={ref}
    className={cn("flex flex-row items-center gap-1", className)}
    {...props}
  />
));
PaginationContent.displayName = "PaginationContent";

const PaginationItem = React.forwardRef<
  HTMLLIElement,
  React.ComponentProps<"li">
>(({ className, ...props }, ref) => (
  <li ref={ref} className={cn("", className)} {...props} />
));
PaginationItem.displayName = "PaginationItem";

type PaginationLinkProps = {
  isActive?: boolean;
} & Pick<ButtonProps, "size"> &
  React.ComponentProps<"a">;

const PaginationLink = ({
  className,
  isActive,
  size = "default",
  ...props
}: PaginationLinkProps) => (
  <a
    aria-current={isActive ? "page" : undefined}
    className={cn(
      buttonVariants({
        variant: isActive ? "outline" : "ghost",
        size,
      }),
      "text-base",
      className
    )}
    {...props}
  />
);
PaginationLink.displayName = "PaginationLink";

const PaginationPrevious = ({
  className,
  ...props
}: React.ComponentProps<typeof PaginationLink>) => (
  <PaginationLink
    aria-label="Go to previous page"
    size="default"
    className={cn("gap-1 pl-2", className)}
    {...props}
  >
    <ChevronLeft className="h-4 w-4" />
    <span>Previous</span>
  </PaginationLink>
);
PaginationPrevious.displayName = "PaginationPrevious";

const PaginationNext = ({
  className,
  ...props
}: React.ComponentProps<typeof PaginationLink>) => (
  <PaginationLink
    aria-label="Go to next page"
    size="default"
    className={cn("gap-1 pr-2", className)}
    {...props}
  >
    <span>Next</span>
    <ChevronRight className="h-4 w-4" />
  </PaginationLink>
);
PaginationNext.displayName = "PaginationNext";

const PaginationEllipsis = ({
  className,
  onPageSelect,
  totalPages,
  isLeft,
  currentPage,
  ...props
}: React.ComponentProps<"span"> & { onPageSelect: (page: number) => void; totalPages: number; isLeft: boolean; currentPage: number }) => {
  const [isDropdownOpen, setIsDropdownOpen] = React.useState(false);

  const handlePageSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const page = parseInt(event.target.value, 10);
    if (!isNaN(page)) {
      onPageSelect(page);
    }
    setIsDropdownOpen(false);
  };

  const getPageOptions = () => {
    if (isLeft) {
      return Array.from({ length: currentPage - 2 }, (_, i) => i + 1);
    } else {
      return Array.from({ length: totalPages - currentPage - 1 }, (_, i) => currentPage + i + 2);
    }
  };

  return (
    <span
      aria-hidden
      className={cn("relative flex h-8 w-8 items-center justify-center", className)}
      {...props}
    >
      <MoreHorizontal className="h-4 w-4 cursor-pointer" onClick={() => setIsDropdownOpen(!isDropdownOpen)} />
      {isDropdownOpen && (
        <select
          className="absolute top-full mt-1 w-16 p-1 border rounded"
          onChange={handlePageSelect}
          onBlur={() => setIsDropdownOpen(false)}
        >
          {getPageOptions().map((page) => (
            <option key={page} value={page}>
              {page}
            </option>
          ))}
        </select>
      )}
      <span className="sr-only">More pages</span>
    </span>
  );
};
PaginationEllipsis.displayName = "PaginationEllipsis";

export {
  Pagination,
  PaginationContent,
  PaginationLink,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
};