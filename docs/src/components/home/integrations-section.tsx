import Heading from "@theme/Heading";
import Link from "@docusaurus/Link";
import { Integration } from "@site/src/components/home/integration";
import { Section } from "@site/src/components/layout/section";
import styles from './integrations-section.module.css';

export function IntegrationsSection() {
  return (
    <Section>
      <Heading as="h2">Plug and play integrations for popular tools</Heading>
      <p className="padding-bottom--lg">Connect your e-commerce stack and get started within 10 minutes.</p>
      <div className="row">
        <Integration name="OpenAI" logo="integrations/openai" />
        <Integration name="Shopify" logo="integrations/shopify" />
        <Integration name="Shopware" logo="integrations/shopware" />
        <Integration name="Medusa" logo="integrations/medusa" />
        <Integration name="Sanity" logo="integrations/sanity" />
        <Integration name="Solidus" logo="integrations/solidus" />
      </div>
      <div className="row">
        <div className={styles.integrationsSectionButtons}>
          <Link className="button button--secondary button--lg" to="/tools/enthusiast/docs/category/plugins">See all integrations</Link>
        </div>
      </div>
    </Section>
  )
}
