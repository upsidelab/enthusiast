import { Cards } from "nextra/components";
import Image from "next/image";

export interface AgentCardProps {
  name: string;
  imageSrc?: string;
  href: string;
}

export default function AgentCard({ name, imageSrc, href }: AgentCardProps) {
  return (
    <Cards.Card title={name} href={href}>
      {imageSrc && (<Image className="x:p-4" src={imageSrc} alt={name} width={512} height={512}/>)}
    </Cards.Card>
  )
}
