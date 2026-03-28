import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["192.168.100.89"],
  experimental: {
    optimizePackageImports: ["react-icons"],
  },
};

export default nextConfig;
