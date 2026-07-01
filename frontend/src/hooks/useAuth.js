/**
 * hooks/useAuth.js — Simple auth state hook.
 *
 * Reads the JWT from localStorage and optionally fetches /me to confirm
 * it's still valid. Provides login, logout, and isAuthenticated helpers.
 *
 * This is intentionally lightweight for Phase 2.
 * Phase 7 (Dashboard) will layer more sophisticated state on top.
 */
import { useState, useEffect, useCallback } from 'react';
import { loginEmployer, registerEmployer, logout as apiLogout, getMe } from '../api/auth';

export function useAuth() {
  const [employer, setEmployer] = useState(null);   // { id, email, created_at } | null
  const [loading, setLoading]   = useState(true);   // true while checking localStorage token

  // On mount: if a token exists, verify it with /me
  useEffect(() => {
    const token = localStorage.getItem('skillbin_token');
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then(setEmployer)
      .catch(() => {
        // Token invalid or expired — clear it
        localStorage.removeItem('skillbin_token');
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    await loginEmployer(email, password);
    const me = await getMe();
    setEmployer(me);
    return me;
  }, []);

  const register = useCallback(async (email, password) => {
    await registerEmployer(email, password);
    // Auto-login after successful registration
    return login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    apiLogout();
    setEmployer(null);
  }, []);

  return {
    employer,
    loading,
    isAuthenticated: employer !== null,
    login,
    register,
    logout,
  };
}
