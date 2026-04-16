import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Lock, Eye, EyeOff, BarChart2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

function getPasswordStrength(pwd) {
  if (!pwd) return { score: 0, label: '' };
  let score = 0;
  if (pwd.length >= 6)  score++;
  if (pwd.length >= 10) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  if (score <= 1) return { score: 1, label: 'Weak' };
  if (score <= 3) return { score: 2, label: 'Medium' };
  return { score: 3, label: 'Strong' };
}

export default function Signup() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const strength = useMemo(() => getPasswordStrength(password), [password]);

  const barClass = (idx) => {
    if (!password) return '';
    if (strength.score >= 3 && idx <= 3) return 'strong';
    if (strength.score === 2 && idx <= 2) return 'medium';
    if (strength.score === 1 && idx === 1) return 'weak';
    return '';
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    try {
      await register(name.trim(), email.trim(), password);
      setSuccess(true);
      setTimeout(() => navigate('/'), 1000);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Brand */}
        <div className="auth-brand">
          <div className="auth-brand-icon">
            <BarChart2 size={22} color="white" strokeWidth={2.5} />
          </div>
          <span className="auth-brand-name">DataLens</span>
        </div>

        {/* Heading */}
        <div className="auth-heading">
          <h1>Create your account</h1>
          <p>Start tracking prices in seconds</p>
        </div>

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          {error && (
            <div className="auth-error">
              <AlertCircle size={15} />
              {error}
            </div>
          )}
          {success && (
            <div className="auth-success">
              <CheckCircle2 size={15} />
              Account created! Redirecting…
            </div>
          )}

          {/* Name */}
          <div className="auth-field">
            <label htmlFor="signup-name">Full Name</label>
            <div className="auth-input-wrap">
              <input
                id="signup-name"
                className="auth-input"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={e => setName(e.target.value)}
                required
                autoComplete="name"
              />
              <User size={16} className="auth-input-icon" />
            </div>
          </div>

          {/* Email */}
          <div className="auth-field">
            <label htmlFor="signup-email">Email</label>
            <div className="auth-input-wrap">
              <input
                id="signup-email"
                className="auth-input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
              <Mail size={16} className="auth-input-icon" />
            </div>
          </div>

          {/* Password */}
          <div className="auth-field">
            <label htmlFor="signup-password">Password</label>
            <div className="auth-input-wrap">
              <input
                id="signup-password"
                className="auth-input"
                type={showPwd ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
              <Lock size={16} className="auth-input-icon" />
              <button
                type="button"
                className="auth-toggle-pwd"
                onClick={() => setShowPwd(v => !v)}
                tabIndex={-1}
                aria-label="Toggle password visibility"
              >
                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            {/* Strength bar */}
            {password && (
              <>
                <div className="pwd-strength">
                  {[1, 2, 3].map(i => (
                    <div key={i} className={`pwd-strength-bar ${barClass(i)}`} />
                  ))}
                </div>
                <p className="pwd-strength-label">{strength.label}</p>
              </>
            )}
          </div>

          {/* Submit */}
          <button
            id="signup-submit"
            type="submit"
            className="auth-submit"
            disabled={loading || success}
          >
            {loading && <span className="auth-spinner" />}
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        {/* Switch to login */}
        <p className="auth-switch" style={{ marginTop: '24px' }}>
          Already have an account?{' '}
          <button onClick={() => navigate('/login')}>Sign in</button>
        </p>
      </div>
    </div>
  );
}
