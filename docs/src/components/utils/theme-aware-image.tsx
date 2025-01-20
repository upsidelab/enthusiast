import style from './theme-aware-image.module.css';
import clsx from "clsx";

export interface ThemeAwareImageProps {
  name: string;
  alt: string;
  className?: string;
}

export function ThemeAwareImage({ name, alt, className }: ThemeAwareImageProps) {
  const lightImageName = `/tools/enthusiast/img/${name}.svg`;
  const darkImageName = `/tools/enthusiast/img/${name}-dark.svg`;

  return (
    <>
      <img className={clsx(style.imageLight, className)} src={lightImageName} alt={alt} />
      <img className={clsx(style.imageDark, className)} src={darkImageName} alt={alt} />
    </>
  )
}
