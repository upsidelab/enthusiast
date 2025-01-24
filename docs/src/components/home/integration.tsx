import clsx from "clsx";
import styles from "./integration.module.css";
import { ThemeAwareImage } from "@site/src/components/utils/theme-aware-image";

export interface IntegrationProps {
  name: string;
  logo: string;
}

export function Integration({ name, logo }: IntegrationProps) {
  return (
    <div className={clsx("col col--4", styles.integration)}>
      <ThemeAwareImage name={logo} alt={name} className={styles.integrationImage} />
    </div>
  )
}
