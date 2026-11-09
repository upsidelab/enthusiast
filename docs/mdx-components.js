import { useMDXComponents as getThemeComponents } from "nextra-theme-docs";
import SiteLink from "./components/site-link";

const themeComponents = getThemeComponents();

export function useMDXComponents(components) {
  return {
    ...themeComponents,
    a: SiteLink,
    ...components
  };
}
