import { Footer, Layout, Navbar } from "nextra-theme-docs";
import { Banner, Head } from "nextra/components";
import { getPageMap } from "nextra/page-map";
import "nextra-theme-docs/style.css";
import Logo from "@/app/logo";

export const metadata = {
  // Define your metadata here
  // For more information on metadata API, see: https://nextjs.org/docs/app/building-your-application/optimizing/metadata
}

const banner = <Banner storageKey="some-key">Nextra 4.0 is released 🎉</Banner>
const navbar = (
  <Navbar
    logo={<Logo/>}
    // ... Your additional navbar options
  />
)
const footer = <Footer>MIT {new Date().getFullYear()} © Nextra.</Footer>

export default async function RootLayout({ children }: any) {
  return (
    <html
      lang="en"
      dir="ltr"
      suppressHydrationWarning
    >
    <Head>
    </Head>
    <body>
    <Layout
      banner={banner}
      navbar={navbar}
      pageMap={await getPageMap("/docs/")}
      docsRepositoryBase="https://github.com/upsidelab/enthusiast/tree/main/docs"
      footer={footer}
      // ... Your additional layout options
    >
      {children}
    </Layout>
    </body>
    </html>
  )
}
