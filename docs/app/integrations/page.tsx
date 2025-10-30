import {Cards} from "nextra/components"
import { useMDXComponents as getMDXComponents } from "../../mdx-components";
import IntegrationCard from "@/components/integration-card";
import { Metadata } from "next";

const mdxComponents = getMDXComponents({});
const Wrapper = mdxComponents.wrapper;
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;

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
      <H2>Language Models</H2>
      <Cards>
        <IntegrationCard name="OpenAI" imageSrc="/tools/enthusiast/img/integrations/openai.png" href="/integrations/openai/" />
        <IntegrationCard name="Ollama" imageSrc="/tools/enthusiast/img/integrations/ollama.png" href="/integrations/ollama/" />
        <IntegrationCard name="Azure OpenAI" imageSrc="/tools/enthusiast/img/integrations/azure-openai.png" href="/integrations/azure-openai/" />
        <IntegrationCard name="Google Gemini" imageSrc="/tools/enthusiast/img/integrations/gemini.png" href="/integrations/gemini/" />
        <IntegrationCard name="Mistral" imageSrc="/tools/enthusiast/img/integrations/mistral.png" href="/integrations/mistral/" />
      </Cards>
    </Wrapper>
  )
}
