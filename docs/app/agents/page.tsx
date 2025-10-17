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
        <IntegrationCard name="Product Search" imageSrc="/tools/enthusiast/img/integrations/placeholder.png" href="/agents/agent-product-search/" />
        <IntegrationCard name="Catalog Enrichment" imageSrc="/tools/enthusiast/img/integrations/placeholder.png" href="/agents/agent-catalog-enrichment/" />
        <IntegrationCard name="OCR Order" imageSrc="/tools/enthusiast/img/integrations/placeholder.png" href="/agents/agent-ocr-order/" />
        <IntegrationCard name="User Manuals" imageSrc="/tools/enthusiast/img/integrations/placeholder.png" href="/agents/agent-customer-support/" />
      </Cards>
    </Wrapper>
  )
}
