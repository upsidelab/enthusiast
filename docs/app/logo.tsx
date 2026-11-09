import styles from "./logo.module.css";
import Image from "next/image";
import Link from "next/link";

export default function Logo() {
  return (
    <Link href="/" className="x:flex x:items-center">
      <Image src="/tools/enthusiast/logo.png" alt="Enthusiast" height={32} width={32} className={styles.logo__image} />
      <b>enthusiast.</b>
    </Link>
  );
}
