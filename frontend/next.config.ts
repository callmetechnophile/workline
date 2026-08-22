import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    unoptimized: true,
  },
  typescript: {
    // Canonical typechecking is handled via TypeScript CLI
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
