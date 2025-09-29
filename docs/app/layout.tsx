import { Footer, Layout, Navbar } from "nextra-theme-docs";
import { Banner, Head } from "nextra/components";
import { getPageMap } from "nextra/page-map";
import "nextra-theme-docs/style.css";
import Logo from "@/app/logo";
import { GoogleTagManager } from "@next/third-parties/google"

export const metadata = {
  // Define your metadata here
  // For more information on metadata API, see: https://nextjs.org/docs/app/building-your-application/optimizing/metadata
}

const banner = <Banner storageKey="banner">Enthusiast 1.3.0 is released 🎉</Banner>
const navbar = <Navbar logo={<Logo/>} projectLink="https://github.com/upsidelab/enthusiast/"/>
const footer = (
  <Footer>
    © {new Date().getFullYear()}&nbsp;
    <a href="https://upsidelab.io">Upside Lab sp. z o.o.</a>
  </Footer>
)

const gtagId = process.env.GTAG_ID;

export default async function RootLayout({ children }: any) {
  return (
    <html
      lang="en"
      dir="ltr"
      suppressHydrationWarning
    >
    <Head>
    </Head>
    {gtagId && <GoogleTagManager gtmId={gtagId}/>}
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
