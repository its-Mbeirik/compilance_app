/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
  async rewrites() {
    return {
      beforeFiles: [
        // Proxy /api/v1/* requests directly to the backend /api/v1/*
        {
          source: '/api/v1/:path*',
          destination: 'http://backend:8000/api/v1/:path*',
        },
      ],
    }
  },
  headers: async () => {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, no-cache, must-revalidate, proxy-revalidate',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
