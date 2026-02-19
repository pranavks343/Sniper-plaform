const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // ⚠️  DO NOT REMOVE — required for Render deployment.
  // Without this, the standalone server bundle is not generated and
  // the app crashes with "clientModules undefined" at runtime.
  output: 'standalone',

  // Required for monorepo: tells Next.js standalone file tracing to include
  // files from the workspace root (where node_modules are hoisted to).
  experimental: {
    outputFileTracingRoot: path.join(__dirname, '../../'),
  },
};

module.exports = nextConfig;
