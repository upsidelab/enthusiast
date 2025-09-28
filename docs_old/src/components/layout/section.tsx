import { ReactNode } from "react";
import styles from './section.module.css';

export interface SectionProps {
  children: ReactNode;
}

export function Section({ children }: SectionProps) {
  return (
    <section className={styles.section}>
      {children}
    </section>
  )
}
