import { Footer, Layout, Navbar } from "nextra-theme-docs";
import { Banner, Head } from "nextra/components";
import { LinkArrowIcon } from "nextra/icons";
import { getPageMap } from "nextra/page-map";
import "nextra-theme-docs/style.css";
import Logo from "@/app/logo";
import { GoogleTagManager } from "@next/third-parties/google"

export const metadata = {
  // Define your metadata here
  // For more information on metadata API, see: https://nextjs.org/docs/app/building-your-application/optimizing/metadata
}

const banner = (
  <Banner storageKey="v1.7-legacy" dismissible={false}>
    You are viewing the documentation for Enthusiast 1.7.{" "}
    {/* A plain anchor: the latest documentation is a separate site, outside this site's basePath. */}
    {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
    <a
      href="/tools/enthusiast/docs"
      className="x:text-primary-600 x:underline x:hover:no-underline x:decoration-from-font x:[text-underline-position:from-font]"
    >
      Go to the latest documentation&nbsp;<LinkArrowIcon height="1em" className="x:inline x:align-baseline x:shrink-0" />
    </a>
  </Banner>
)

const navbar = <Navbar logo={<Logo/>} logoLink={false} align="left" projectLink="https://github.com/upsidelab/enthusiast/"/>
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
      pageMap={await getPageMap("/")}
      docsRepositoryBase="https://github.com/upsidelab/enthusiast/tree/main/docs-v1.7"
      footer={footer}
      // ... Your additional layout options
    >
      {children}
    </Layout>
    </body>
    </html>
  )
}
