import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // @databricks/sql loads native modules (lz4-napi, its kernel); Turbopack can't bundle them.
  serverExternalPackages: ["@databricks/sql"],
};

export default nextConfig;
