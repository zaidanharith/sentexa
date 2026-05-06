import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["192.168.100.89"],
  experimental: {
    optimizePackageImports: ["react-icons"],
  },
  turbopack: {
    resolveAlias: {},
  },
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
      ignored: ["**\\node_modules/**", "**\\.git/**"],
    };
    return config;
  },
};

export default nextConfig;
