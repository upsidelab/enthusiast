import type { NextConfig } from "next";
import nextra from "nextra";

const nextConfig: NextConfig = {};

const withNextra = nextra({
  contentDirBasePath: '/docs'
});

export default withNextra(nextConfig);
