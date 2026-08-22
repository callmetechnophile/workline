import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname, ".."),
  },
  images: {
    unoptimized: true,
  },
  typescript: {
    // Canonical typechecking is handled via TypeScript CLI
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
