import type { NextConfig } from "next";
import nextra from "nextra";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/tools/enthusiast/v1.7",
  env: {
    GTAG_ID: process.env.GTAG_ID,
  },
  images: {
    unoptimized: true,
  },
  trailingSlash: false,
};

const withNextra = nextra({});

export default withNextra(nextConfig);
