import {Cards} from "nextra/components"
import { useMDXComponents as getMDXComponents } from "../../mdx-components";

const mdxComponents = getMDXComponents({});
const Wrapper = mdxComponents.wrapper;
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;

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
        <Cards.Card title="Medusa" href="/integrations/medusa/"/>
        <Cards.Card title="Shopware" href="/integrations/shopware/"/>
        <Cards.Card title="Shopify" href="/integrations/shopify/"/>
        <Cards.Card title="Solidus" href="/integrations/solidus/"/>
      </Cards>
      <H2>Content Management Systems</H2>
      <Cards>
        <Cards.Card title="Sanity" href="/integrations/sanity/"/>
        <Cards.Card title="wordpress" href="/integrations/wordpress/"/>
      </Cards>
      <H2>Language Models</H2>
      <Cards>
        <Cards.Card title="OpenAI" href="/integrations/openai/"/>
        <Cards.Card title="Ollama" href="/integrations/ollama/"/>
        <Cards.Card title="Azure OpenAI" href="/integrations/azure-openai/"/>
        <Cards.Card title="Google Gemini" href="/integrations/gemini/"/>
        <Cards.Card title="Mistral" href="/integrations/mistral/"/>
      </Cards>
    </Wrapper>
  )
}
