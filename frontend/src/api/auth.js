/**
 * api/auth.js — Auth API calls.
 *
 * All calls go through the shared apiClient (base URL + JWT interceptor).
 * Functions return the response data directly and let callers handle errors.
 */
import apiClient from './client';

/**
 * Register a new employer.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{id, email, created_at}>}
 */
export async function registerEmployer(email, password) {
  const { data } = await apiClient.post('/api/v1/auth/register', { email, password });
  return data;
}

/**
 * Login and receive a JWT token.
 * Stores the token in localStorage on success.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{access_token, token_type, expires_in}>}
 */
export async function loginEmployer(email, password) {
  const { data } = await apiClient.post('/api/v1/auth/login', { email, password });
  localStorage.setItem('skillbin_token', data.access_token);
  return data;
}

/**
 * Fetch the authenticated employer's profile.
 * Used to verify token validity and display the logged-in email.
 * @returns {Promise<{id, email, created_at}>}
 */
export async function getMe() {
  const { data } = await apiClient.get('/api/v1/auth/me');
  return data;
}

/**
 * Clear the stored token (client-side logout).
 * Backend JWTs are stateless — no server-side invalidation in v1.
 */
export function logout() {
  localStorage.removeItem('skillbin_token');
}
