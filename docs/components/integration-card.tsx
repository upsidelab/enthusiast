import { Cards } from "nextra/components";
import Image from "next/image";

export interface IntegrationCardProps {
  name: string;
  imageSrc: string;
  href: string;
}

export default function IntegrationCard({ name, imageSrc, href }: IntegrationCardProps) {
  return (
    <Cards.Card title={name} href={href}>
      <Image className="x:p-4" src={imageSrc} alt={name} width={196} height={196} />
    </Cards.Card>
  )
}
