import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, AlertCircle, ArrowRight } from 'lucide-react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.post('/auth/login', { email, password });
      login(res.data.access_token, {
        id: res.data.user_id,
        email: res.data.email,
        full_name: res.data.full_name,
        role: res.data.role,
        is_active: true,
        created_at: new Date().toISOString(),
      });
      navigate('/documents');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sign in. Please verify your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleAdminDemoFill = () => {
    setEmail('admin@clauseguard.local');
    setPassword('AdminSecurePass123!');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-8 glass-panel p-8 rounded-3xl border border-beige-200 dark:border-slate-800 shadow-xl relative">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto text-white shadow-sm">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold text-beige-950 dark:text-white">Welcome back</h2>
          <p className="text-xs text-beige-600 dark:text-slate-400">Sign in to your ClauseGuard account</p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/20 dark:text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-beige-800 dark:text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-beige-400 dark:text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700/80 text-sm text-beige-900 dark:text-white placeholder-beige-400 dark:placeholder-slate-500 focus:outline-none focus:border-brand-600 transition-colors shadow-sm"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-beige-800 dark:text-slate-300">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-beige-400 dark:text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-beige-300 dark:border-slate-700/80 text-sm text-beige-900 dark:text-white placeholder-beige-400 dark:placeholder-slate-500 focus:outline-none focus:border-brand-600 transition-colors shadow-sm"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <span>Signing in...</span> : <span>Sign In</span>}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="pt-2 border-t border-beige-200 dark:border-slate-800/80 flex items-center justify-between text-xs">
          <button
            type="button"
            onClick={handleAdminDemoFill}
            className="text-brand-600 dark:text-indigo-400 hover:underline font-semibold"
          >
            Fill Admin Credentials
          </button>
          <Link to="/register" className="text-beige-600 dark:text-slate-400 hover:text-beige-950 dark:hover:text-white font-medium">
            Need an account? Register
          </Link>
        </div>
      </div>
    </div>
  );
};
