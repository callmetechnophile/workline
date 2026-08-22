import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    unoptimized: true,
  },
  typescript: {
    // Canonical typechecking is handled via TypeScript 7 CLI (npm run typecheck / tsc --noEmit)
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
