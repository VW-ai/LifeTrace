// Allow optional static export for GitHub Pages and similar static hosts.
// Configure via env at build time:
// - STATIC_EXPORT=true to enable `next export`
// - NEXT_PUBLIC_BASE_PATH=/your-repo for project pages (empty for user/org pages)

const isStaticExport = process.env.STATIC_EXPORT === 'true';
let basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
if (basePath && !basePath.startsWith('/')) basePath = `/${basePath}`;

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export on demand
  output: isStaticExport ? 'export' : undefined,
  // Base path for GitHub Pages project sites
  basePath: basePath || undefined,
  assetPrefix: basePath ? `${basePath}/` : undefined,
  // Trailing slash helps GH Pages serve nested routes as directories
  trailingSlash: isStaticExport ? true : undefined,
};

export default nextConfig;
