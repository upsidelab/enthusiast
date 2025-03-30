import React from 'react';

export interface FeaturePageContent {
  meta: {
    title: string;
    description: string;
  };
  hero: {
    title: string;
    subtitle: string;
  };
  problem: {
    title: string;
    points: string[];
  };
  solution: {
    title: string;
    description: string;
  };
  howItWorks: {
    title: string;
    subtitle: string;
    steps: string[];
  };
  benefits: {
    title: string;
    items: Array<{
      title: string;
      description: string;
    }>;
  };
  useCase: {
    title: string;
    subtitle: string;
    description: string;
  };
  technical: {
    title: string;
    subtitle: string;
    features: string[];
  };
  cta: {
    title: string;
    description: string;
  };
  faq: {
    title: string;
    questions: Array<{
      question: string;
      answer: string;
    }>;
  };
  footerCta: {
    title: string;
  };
}

export function FeaturePageLayout({ content }: { content: FeaturePageContent }) {
  return (
    <article>
      <h1>{content.hero.title}</h1>

      <export
        meta={content.meta}
      />

      <p>{content.hero.subtitle}</p>

      <div className="cta-buttons">
        <a href="/contact" className="button button--primary">Schedule a Demo</a>
        <a href="https://github.com/upsidelab/enthusiast" className="button button--secondary">View on GitHub</a>
      </div>

      <h2>{content.problem.title}</h2>
      <ul>
        {content.problem.points.map((point, index) => (
          <li key={index}>{point}</li>
        ))}
      </ul>

      <h2>{content.solution.title}</h2>
      <p>{content.solution.description}</p>

      <h2>{content.howItWorks.title}</h2>
      <h3>{content.howItWorks.subtitle}</h3>
      <ol>
        {content.howItWorks.steps.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ol>

      <h2>{content.benefits.title}</h2>
      {content.benefits.items.map((benefit, index) => (
        <p key={index}>
          <strong>{benefit.title}</strong>: {benefit.description}
        </p>
      ))}

      <h2>{content.useCase.title}</h2>
      <h3>{content.useCase.subtitle}</h3>
      <p>{content.useCase.description}</p>

      <h2>{content.technical.title}</h2>
      <h3>{content.technical.subtitle}</h3>
      <ul>
        {content.technical.features.map((feature, index) => (
          <li key={index}>{feature}</li>
        ))}
      </ul>

      <h2>{content.cta.title}</h2>
      <p>{content.cta.description}</p>

      <div className="cta-section">
        <a href="/contact" className="button button--primary">Schedule a Demo</a>
        <a href="https://github.com/upsidelab/enthusiast" className="button button--secondary">View on GitHub</a>
      </div>

      <h2>{content.faq.title}</h2>
      {content.faq.questions.map((faq, index) => (
        <div key={index}>
          <h3>{faq.question}</h3>
          <p>{faq.answer}</p>
        </div>
      ))}

      <div className="footer-cta">
        <h3>{content.footerCta.title}</h3>
        <a href="/contact" className="button button--primary">Schedule a Demo</a>
      </div>
    </article>
  );
} 
