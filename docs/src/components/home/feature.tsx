import clsx from "clsx";
import Heading from "@theme/Heading";

export interface FeatureProps {
  title: string;
  description: string;
}

export function Feature({ title, description }: FeatureProps) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  )
}
