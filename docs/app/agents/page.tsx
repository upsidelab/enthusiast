import {Cards} from "nextra/components"
import { useMDXComponents as getMDXComponents } from "../../mdx-components";
import IntegrationCard from "@/components/integration-card";

const mdxComponents = getMDXComponents({});
const Wrapper = mdxComponents.wrapper;
const H2 = mdxComponents.h2;

export default async function Page() {
  const metadata = {
    title: "Prebuilt Agents | Enthusiast",
    description: "",
  }
  return (
    <Wrapper toc={[]} metadata={metadata} sourceCode={""} >
      <H2>Example agents</H2>
      <Cards>
        <IntegrationCard name="Product Search" href="/agents/agent-product-search/" />
        <IntegrationCard name="Catalog Enrichment" href="/agents/agent-catalog-enrichment/" />
        <IntegrationCard name="OCR Order" href="/agents/agent-ocr-order/" />
        <IntegrationCard name="User Manuals" href="/agents/agent-customer-support/" />
      </Cards>
    </Wrapper>
  )
}
