import styles from "./logo.module.css";
import Image from "next/image";

export default function Logo() {
  return (
    <a href="https://upsidelab.io/tools/enthusiast" className="x:flex x:items-center">
      <Image src="/tools/enthusiast/logo.png" alt="Enthusiast" height={32} width={32} className={styles.logo__image} />
      <b>enthusiast.</b>
    </a>
  );
}
