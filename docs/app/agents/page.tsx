import { Cards } from "nextra/components"
import { useMDXComponents as getMDXComponents } from "../../mdx-components";
import { Metadata } from "next";
import AgentCard from "@/components/agent-card";

const mdxComponents = getMDXComponents({});
const Wrapper = mdxComponents.wrapper;
const H1 = mdxComponents.h1;
const P = mdxComponents.p;

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
      <P>Enthusiast comes with a bunch of pre-built agents that cover many common use cases for back-office operations, such as enhancing product data, searching internal documentation, and processing business documents.</P>
      <P>This curated library allows you to quickly deploy specialized AI solutions for automation and productivity without needing to build custom agents from scratch. Furthermore, these agents can be customized and extended by a developer to precisely adjust their behavior and integrate with your business workflows.</P>
      <Cards className="x:py-4" num={2}>
        <AgentCard name="Product Search" imageSrc="/tools/enthusiast/img/agents/product-search.png" href="/agents/product-search/" />
        <AgentCard name="Catalog Enrichment" imageSrc="/tools/enthusiast/img/agents/catalog-enrichment.png" href="/agents/catalog-enrichment/" />
        <AgentCard name="Purchase Order OCR" imageSrc="/tools/enthusiast/img/agents/purchase-order-ocr.png" href="/agents/purchase-order-ocr/" />
        <AgentCard name="User Manual Search" imageSrc="/tools/enthusiast/img/agents/user-manual-search.png" href="/agents/user-manual-search/" />
      </Cards>
    </Wrapper>
  )
}
