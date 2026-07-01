import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './LoginPage.css';

/* ── Subcomponents ──────────────────────────────────────────────────────────── */

function EyeIcon({ visible }) {
  return visible ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}

function Spinner() {
  return <span className="login-spinner" aria-hidden="true" />;
}

/* ── Main page ──────────────────────────────────────────────────────────────── */

export default function LoginPage() {
  const navigate  = useNavigate();
  const { login, register } = useAuth();

  const [mode,        setMode]        = useState('login');   // 'login' | 'register'
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [showPwd,     setShowPwd]     = useState(false);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');
  const [successMsg,  setSuccessMsg]  = useState('');

  const isLogin = mode === 'login';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
        navigate('/');
      } else {
        await register(email, password);
        setSuccessMsg('Account created! You are now logged in.');
        setTimeout(() => navigate('/'), 1200);
      }
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;

      if (status === 409)       setError('This email is already registered. Try logging in.');
      else if (status === 401)  setError('Invalid email or password.');
      else if (status === 422)  setError('Please enter a valid email address.');
      else if (status === 429)  setError('Too many attempts — please wait a minute.');
      else                      setError(detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-root">
      {/* Background glow */}
      <div className="login-glow" aria-hidden="true" />

      <div className="login-card glass-card" role="main">
        {/* Logo */}
        <Link to="/" className="login-logo" aria-label="SkillBin home">
          <span className="login-logo-icon" aria-hidden="true">⬡</span>
          <span className="login-logo-text">SkillBin</span>
        </Link>

        {/* Mode toggle */}
        <div className="login-tabs" role="tablist">
          <button
            id="tab-login"
            role="tab"
            aria-selected={isLogin}
            className={`login-tab ${isLogin ? 'login-tab--active' : ''}`}
            onClick={() => { setMode('login'); setError(''); setSuccessMsg(''); }}
          >
            Sign In
          </button>
          <button
            id="tab-register"
            role="tab"
            aria-selected={!isLogin}
            className={`login-tab ${!isLogin ? 'login-tab--active' : ''}`}
            onClick={() => { setMode('register'); setError(''); setSuccessMsg(''); }}
          >
            Register
          </button>
        </div>

        <h1 className="login-heading">
          {isLogin ? 'Welcome back' : 'Create your account'}
        </h1>
        <p className="login-subheading">
          {isLogin
            ? 'Sign in to manage your team and tasks.'
            : 'Set up SkillBin for your team in minutes.'}
        </p>

        {/* Form */}
        <form
          id="auth-form"
          className="login-form"
          onSubmit={handleSubmit}
          aria-labelledby={isLogin ? 'tab-login' : 'tab-register'}
          noValidate
        >
          <div className="form-group">
            <label htmlFor="auth-email" className="form-label">Email</label>
            <input
              id="auth-email"
              type="email"
              autoComplete="email"
              className="form-input"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="auth-password" className="form-label">
              Password
              {!isLogin && (
                <span className="form-hint"> (min. 8 characters)</span>
              )}
            </label>
            <div className="input-wrapper">
              <input
                id="auth-password"
                type={showPwd ? 'text' : 'password'}
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                className="form-input form-input--password"
                placeholder={isLogin ? '••••••••' : 'At least 8 characters'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
              <button
                type="button"
                id="toggle-password"
                className="input-eye-btn"
                onClick={() => setShowPwd((v) => !v)}
                aria-label={showPwd ? 'Hide password' : 'Show password'}
              >
                <EyeIcon visible={showPwd} />
              </button>
            </div>
          </div>

          {/* Feedback messages */}
          {error && (
            <div className="form-error" role="alert" aria-live="assertive">
              <span aria-hidden="true">⚠ </span>{error}
            </div>
          )}
          {successMsg && (
            <div className="form-success" role="status" aria-live="polite">
              <span aria-hidden="true">✓ </span>{successMsg}
            </div>
          )}

          <button
            id="auth-submit-btn"
            type="submit"
            className="btn-primary login-submit"
            disabled={loading || !email || !password}
          >
            {loading ? <Spinner /> : null}
            {loading
              ? (isLogin ? 'Signing in…' : 'Creating account…')
              : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <p className="login-footer-text">
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <button
            className="login-switch-btn"
            onClick={() => { setMode(isLogin ? 'register' : 'login'); setError(''); }}
          >
            {isLogin ? 'Register' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}
