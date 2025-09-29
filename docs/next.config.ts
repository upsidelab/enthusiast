import type { NextConfig } from "next";
import nextra from "nextra";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/tools/enthusiast",
  env: {
    GTAG_ID: process.env.GTAG_ID,
  },
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

const withNextra = nextra({
  contentDirBasePath: "/docs",
});

export default withNextra(nextConfig);
