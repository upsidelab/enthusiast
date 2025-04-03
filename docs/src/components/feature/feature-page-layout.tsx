import useBaseUrl from '@docusaurus/useBaseUrl'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import './feature-page-layout.css'

interface FeaturePageContent {
  meta: {
    title: string
    description: string
  }
  hero: {
    title: string
    subtitle: string
  }
  problem: {
    title: string
    points: string[]
  }
  solution: {
    title: string
    description: string
  }
  howItWorks: {
    title: string
    subtitle: string
    steps: string[]
  }
  benefits: {
    title: string
    items: Array<{
      title: string
      description: string
    }>
  }
  technical: {
    title: string
    subtitle: string
    features: string[]
  }
  cta: {
    title: string
    description: string
  }
  faq: {
    title: string
    questions: Array<{
      question: string
      answer: string
    }>
  }
  footerCta: {
    title: string
  }
}

interface SectionHeaderProps {
  title: string
  subtitle?: string
}

function SectionHeader({ title, subtitle }: SectionHeaderProps) {
  return (
    <>
      <h2 className="feature-section__title">{title}</h2>
      {subtitle && <h3 className="feature-section__subtitle">{subtitle}</h3>}
    </>
  )
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className={`feature-faq__item ${isOpen ? 'feature-faq__item--open' : ''}`} onClick={() => setIsOpen(!isOpen)}>
      <div className="feature-faq__question-wrapper">
        <h3 className="feature-faq__question">{question}</h3>
        <button className="feature-faq__toggle" aria-label={isOpen ? 'Close answer' : 'Open answer'}>
          {isOpen ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
        </button>
      </div>
      <div className={`feature-faq__answer ${isOpen ? 'feature-faq__answer--visible' : ''}`}>
        <p>{answer}</p>
      </div>
    </div>
  )
}

export function FeaturePageLayout({ content }: { content: FeaturePageContent }) {
  const logoUrl = useBaseUrl('/img/logo.svg')
  const logo3dUrl = useBaseUrl('/img/logo-3d.png')

  return (
    <article className="feature-page">
      <section className="feature-hero">
        <div className="feature-hero__background" />
        <div className="feature-hero__container">
          <div className="feature-hero__content">
            <h1 className="feature-hero__title">{content.hero.title}</h1>
            <p className="feature-hero__subtitle">{content.hero.subtitle}</p>
            <div className="feature-cta feature-cta--center">
              <a href="/contact" className="button button--primary button--lg">
                Schedule a Demo
              </a>
              <a href="https://github.com/upsidelab/enthusiast" className="button button--secondary button--lg">
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      <div className="feature-main">
        <div className="feature-container">
          <section className="feature-section feature-problem">
            <SectionHeader title={content.problem.title} />
            <div className="feature-problem__grid">
              {content.problem.points.map((point, index) => (
                <div key={index} className="feature-problem__item">
                  <p>{point}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="feature-section feature-solution">
            <SectionHeader title={content.solution.title} />
            <p className="feature-section__description">{content.solution.description}</p>
          </section>

          <section className="feature-section feature-steps">
            <SectionHeader title={content.howItWorks.title} subtitle={content.howItWorks.subtitle} />
            <div className="feature-steps__grid">
              {content.howItWorks.steps.map((step, index) => (
                <div key={index} className="feature-steps__item">
                  <div className="feature-steps__number">{index + 1}</div>
                  <p>{step}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="feature-section feature-benefits">
            <SectionHeader title={content.benefits.title} />
            <div className="feature-benefits__grid">
              {content.benefits.items.map((benefit, index) => (
                <div key={index} className="feature-benefits__item">
                  <h3>{benefit.title}</h3>
                  <p>{benefit.description}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="feature-section feature-technical">
            <SectionHeader title={content.technical.title} subtitle={content.technical.subtitle} />
            <div className="feature-technical__grid">
              {content.technical.features.map((feature, index) => (
                <div key={index} className="feature-technical__item">
                  <p>{feature}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="feature-section feature-faq">
            <SectionHeader title={content.faq.title} />
            <div className="feature-faq__grid">
              {content.faq.questions.map((faq, index) => (
                <FAQItem key={index} {...faq} />
              ))}
            </div>
          </section>

          <section className="feature-banner">
            <div className="feature-banner__content">
              <div className="feature-banner__text">
                <h2 className="feature-banner__title">{content.cta.title}</h2>
                <p className="feature-banner__description">{content.cta.description}</p>
                <a href="/contact" className="button button--primary button--lg">
                  Schedule a demo
                </a>
              </div>
              <div className="feature-banner__visual">
                <img
                  src={logo3dUrl}
                  alt="3D Logo"
                  className="feature-banner__logo"
                  onError={(e) => {
                    e.currentTarget.onerror = null
                    e.currentTarget.src = logoUrl
                    e.currentTarget.className = 'feature-banner__logo--fallback'
                  }}
                />
              </div>
            </div>
          </section>

          <section className="feature-footer-cta">
            <h3 className="feature-footer-cta__title">{content.footerCta.title}</h3>
          </section>
        </div>
      </div>
    </article>
  )
}
