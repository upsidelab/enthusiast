import type { NextConfig } from "next";
import nextra from "nextra";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/tools/enthusiast",
};

const withNextra = nextra({
  contentDirBasePath: "/docs",
});

export default withNextra(nextConfig);
