// Centralized API configuration supporting VITE_API_BASE_URL for Vercel production deployments
// Defaults to http://127.0.0.1:8000 for local development
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
