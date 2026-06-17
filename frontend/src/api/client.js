/**
 * api/client.js — Axios instance with shared config.
 *
 * All API calls go through this client so that:
 * - The base URL is set from the Vite env var (never hardcoded).
 * - JWT tokens are attached automatically to every request.
 * - 401 responses redirect to /login globally (Phase 2).
 * - A consistent timeout is enforced (mirrors the backend's 30s Claude timeout).
 */
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 35_000, // 35 s — covers the backend's 30 s Claude API timeout + headroom
});

// ── Request interceptor: attach stored JWT token ──────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('skillbin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor: handle auth expiry globally ────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and redirect to login
      localStorage.removeItem('skillbin_token');
      window.location.href = '/login';
    }
    // Propagate all other errors for per-call handling
    return Promise.reject(error);
  },
);

export default apiClient;
