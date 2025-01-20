import Heading from "@theme/Heading";
import { Feature } from "@site/src/components/home/feature";
import { Section } from "@site/src/components/layout/section";

export function FeaturesSection() {
  return (
    <Section>
      <Heading as="h2">10x your e-commerce team</Heading>
      <div className="row padding-top--lg">
        <Feature title="Customer Support" description="(Semi-)automate responses to customer questions. Enthusiast can find answers from your product data." />
        <Feature title="Knowledge Base" description="For companies with complex catalogs, Enthusiast supports sales teams with detailed product knowledge." />
        <Feature title="Marketing Content" description="Generate newsletters, blog posts, and ads. Enthusiast acts as a marketer, creating content at scale from day one." />
      </div>
    </Section>
  )
}
