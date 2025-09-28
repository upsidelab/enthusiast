import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';
import { IntegrationsSection } from "@site/src/components/home/integrations-section";
import { FeaturesSection } from "@site/src/components/home/features-section";
import { OpenSourceSection } from "@site/src/components/home/open-source-section";
import { ThemeAwareImage } from "@site/src/components/utils/theme-aware-image";
import { RagSection } from "@site/src/components/home/rag-section";

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          <ThemeAwareImage name="logo" alt="Enthusiast" className={styles.heroLogo} />
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg margin-horiz--md"
            to="/docs/">
            Browse Documentation
          </Link>
          <Link
            className="button button--primary button--lg margin-horiz--md"
            to="/docs/getting-started/installation">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): JSX.Element {
  return (
    <Layout
      title={`Home`}
      description="Your E-Commerce AI Agent">
      <HomepageHeader />
      <div className={styles.container}>
        <FeaturesSection />
        <IntegrationsSection />
        <RagSection />
        <OpenSourceSection />
      </div>
    </Layout>
  );
}
