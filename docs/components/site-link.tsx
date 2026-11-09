import type { ComponentProps } from "react";
import { Link as ThemeLink } from "nextra-theme-docs";

/**
 * Paths served by other documentation sites on the same domain: the Suvereo docs and the frozen Enthusiast 1.7 docs.
 * Links to them are written relative to the current page (for example `../../suvereo/docs/...`), so they work on every
 * domain the docs are hosted on.
 */
const OTHER_SITE_PATH = /^(\.\.\/)+(suvereo|tools\/enthusiast\/v1\.7)(\/|$)/;

/** The theme's link styling, for anchors rendered outside the theme's `Link`. */
export const LINK_CLASS_NAME =
  "x:text-primary-600 x:underline x:hover:no-underline x:decoration-from-font x:[text-underline-position:from-font]";

/**
 * Whether `href` points to another documentation site on the same domain.
 *
 * @param href - The link target.
 * @returns `true` for relative paths to the Suvereo or Enthusiast 1.7 docs.
 */
export function isOtherSitePath(href: unknown): href is string {
  return typeof href === "string" && OTHER_SITE_PATH.test(href);
}

/**
 * Link used for all Markdown links. Links to the other documentation sites are rendered as plain anchors: they are
 * outside this Next.js app, so they must not be handled by its client-side router.
 * All other links use the theme's `Link`.
 */
export default function SiteLink({ href, className, ...props }: ComponentProps<"a">) {
  if (isOtherSitePath(href)) {
    return <a href={href} className={[LINK_CLASS_NAME, className].filter(Boolean).join(" ")} {...props} />;
  }
  return <ThemeLink href={href ?? ""} className={className} {...props} />;
}
