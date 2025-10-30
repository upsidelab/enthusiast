import {Cards} from "nextra/components"
import { useMDXComponents as getMDXComponents } from "../../mdx-components";
import IntegrationCard from "@/components/integration-card";
import { Metadata } from "next";

const mdxComponents = getMDXComponents({});
const Wrapper = mdxComponents.wrapper;
const H1 = mdxComponents.h1;

export const metadata: Metadata = {
  title: "Pre-built Agents | Enthusiast",
}

export default async function Page() {
  const metadata = {
    title: "Pre-built Agents | Enthusiast",
    description: "",
  }
  return (
    <Wrapper toc={[]} metadata={metadata} sourceCode={""} >
      <H1>Pre-built Agents</H1>
      <Cards>
        <IntegrationCard name="Product Search" href="/agents/agent-product-search/" />
        <IntegrationCard name="Catalog Enrichment" href="/agents/agent-catalog-enrichment/" />
        <IntegrationCard name="OCR Order" href="/agents/agent-ocr-order/" />
        <IntegrationCard name="User Manuals" href="/agents/agent-customer-support/" />
      </Cards>
    </Wrapper>
  )
}
