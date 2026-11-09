import { Cards } from "nextra/components";
import { isOtherSitePath } from "@/components/site-link";

export interface SiteCardProps {
  title: string;
  href: string;
  className?: string;
}

/**
 * A card with an arrow, like `Cards.Card`. `Cards.Card` always renders a Next.js link, so cards pointing to another
 * documentation site on the same domain render a plain anchor with the same styling instead.
 */
export default function SiteCard({ title, href, className }: SiteCardProps) {
  if (!isOtherSitePath(href)) {
    return <Cards.Card className={className} title={title} href={href} arrow />;
  }
  return (
    <a
      href={href}
      className={[
        "x:group x:focus-visible:nextra-focus nextra-card x:flex x:flex-col x:justify-start x:overflow-hidden x:rounded-lg x:border x:border-gray-200",
        "x:text-current x:no-underline x:dark:shadow-none x:hover:shadow-gray-100 x:dark:hover:shadow-none x:shadow-gray-100",
        "x:active:shadow-sm x:active:shadow-gray-200 x:transition-all x:duration-200 x:hover:border-gray-300",
        "x:bg-transparent x:shadow-sm x:dark:border-neutral-800 x:hover:bg-slate-50 x:hover:shadow-md x:dark:hover:border-neutral-700 x:dark:hover:bg-neutral-900",
        className,
      ].filter(Boolean).join(" ")}
    >
      <span
        className={[
          "x:flex x:font-semibold x:items-center x:gap-2 x:p-4 x:text-gray-700 x:hover:text-gray-900",
          'x:after:content-["→"] x:after:transition-transform x:after:duration-75 x:group-hover:after:translate-x-0.5 x:group-focus:after:translate-x-0.5',
          "x:dark:text-neutral-200 x:dark:hover:text-neutral-50",
        ].join(" ")}
        title={title}
      >
        <span className="_truncate">{title}</span>
      </span>
    </a>
  );
}
