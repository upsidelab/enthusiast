import {Cards} from "nextra/components"
import { useMDXComponents as getMDXComponents } from "../../mdx-components";
import IntegrationCard from "@/components/integration-card";
import { Metadata } from "next";

const mdxComponents = getMDXComponents({});
const Wrapper = mdxComponents.wrapper;
const P = mdxComponents.p;
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;
const A = mdxComponents.a;

export const metadata: Metadata = {
  title: "Integrations | Enthusiast",
}

export default async function Page() {
  const metadata = {
    title: "Integrations | Enthusiast",
    description: "",
  }
  return (
    <Wrapper toc={[]} metadata={metadata} sourceCode={""} >
      <H1>Integrations</H1>
      <P>Enthusiast comes with a set of ready-to-use integrations that connect your agents to major e-commerce platforms and content management systems.</P>
      <P>They allow you to immediately enable your agents to connect to product catalogs and documents. Furthermore, each of these integrations can be customized and extended by a developer to reflect the structure of the data in your systems.</P>
      <P>Language model providers (such as OpenAI, Anthropic, Gemini or Azure OpenAI) are provided by Suvereo. See the <A href="https://upsidelab.io/tools/suvereo/integrations">Suvereo integrations</A> for the full list.</P>
      <P>Looking for the Enthusiast 1.7 integrations? See the <A href="https://upsidelab.io/tools/enthusiast/v1.7/integrations">Enthusiast 1.7 documentation</A>.</P>
      <H2>E-Commerce Systems</H2>
      <Cards>
        <IntegrationCard name="Medusa" imageSrc="/tools/enthusiast/img/integrations/medusa.png" href="/integrations/medusa/" />
        <IntegrationCard name="Shopware" imageSrc="/tools/enthusiast/img/integrations/shopware.png" href="/integrations/shopware/" />
        <IntegrationCard name="Shopify" imageSrc="/tools/enthusiast/img/integrations/shopify.png" href="/integrations/shopify/" />
        <IntegrationCard name="Solidus" imageSrc="/tools/enthusiast/img/integrations/solidus.png" href="/integrations/solidus/" />
        <IntegrationCard name="WooCommerce" imageSrc="/tools/enthusiast/img/integrations/woocommerce.png" href="/integrations/woocommerce/" />
      </Cards>
      <H2>Content Management Systems</H2>
      <Cards>
        <IntegrationCard name="Sanity" imageSrc="/tools/enthusiast/img/integrations/sanity.png" href="/integrations/sanity/" />
        <IntegrationCard name="WordPress" imageSrc="/tools/enthusiast/img/integrations/wordpress.png" href="/integrations/wordpress/" />
      </Cards>
    </Wrapper>
  )
}
