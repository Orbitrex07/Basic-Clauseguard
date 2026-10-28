import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Shield, Upload, FileText, Settings, LogOut, ChevronDown, UserCheck, Scale, BarChart2, Sun, Moon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const Navbar: React.FC = () => {
  const { user, isAdmin, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [adminOpen, setAdminOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="border-b border-beige-200 dark:border-slate-800 bg-beige-50/90 dark:bg-slate-950/90 backdrop-blur-md sticky top-0 z-40 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-sm group-hover:bg-brand-700 transition-colors">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-extrabold tracking-tight text-beige-900 dark:text-white flex items-center gap-1.5">
                Clause<span className="text-brand-600 dark:text-brand-400">Guard</span>
              </span>
              <span className="block text-[10px] uppercase font-bold tracking-widest text-beige-600 dark:text-slate-400 -mt-1">
                AI Contract Safety
              </span>
            </div>
          </Link>

          {/* Center Navigation Links */}
          {user && (
            <div className="hidden md:flex items-center gap-1.5">
              <Link
                to="/documents"
                className={`px-3 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2 ${
                  isActive('/documents')
                    ? 'bg-beige-200/80 text-brand-700 dark:bg-slate-800 dark:text-indigo-400 font-semibold'
                    : 'text-beige-700 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-900'
                }`}
              >
                <FileText className="w-4 h-4" />
                Contracts
              </Link>

              <Link
                to="/upload"
                className={`px-3 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2 ${
                  isActive('/upload')
                    ? 'bg-beige-200/80 text-brand-700 dark:bg-slate-800 dark:text-indigo-400 font-semibold'
                    : 'text-beige-700 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-900'
                }`}
              >
                <Upload className="w-4 h-4" />
                Analyze Contract
              </Link>

              {isAdmin && (
                <div className="relative">
                  <button
                    onClick={() => setAdminOpen(!adminOpen)}
                    className="px-3 py-2 rounded-xl text-sm font-medium text-beige-700 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-900 transition-colors flex items-center gap-1.5"
                  >
                    <Settings className="w-4 h-4 text-brand-600 dark:text-indigo-400" />
                    <span>Admin</span>
                    <ChevronDown className="w-3.5 h-3.5 opacity-60" />
                  </button>

                  {adminOpen && (
                    <div
                      onMouseLeave={() => setAdminOpen(false)}
                      className="absolute left-0 mt-1 w-52 rounded-xl bg-white dark:bg-slate-900 border border-beige-200 dark:border-slate-800 shadow-xl py-1.5 z-50 text-xs"
                    >
                      <Link
                        to="/admin/review"
                        onClick={() => setAdminOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2 text-beige-800 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800 font-medium"
                      >
                        <UserCheck className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        Review Queue
                      </Link>
                      <Link
                        to="/admin/rules"
                        onClick={() => setAdminOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2 text-beige-800 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800 font-medium"
                      >
                        <Scale className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                        Risk Rules Editor
                      </Link>
                      <Link
                        to="/admin/audit"
                        onClick={() => setAdminOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2 text-beige-800 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800 font-medium"
                      >
                        <FileText className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                        Audit Logs
                      </Link>
                      <Link
                        to="/admin/stats"
                        onClick={() => setAdminOpen(false)}
                        className="flex items-center gap-2.5 px-4 py-2 text-beige-800 hover:text-beige-950 hover:bg-beige-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800 font-medium"
                      >
                        <BarChart2 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                        System Statistics
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Right Action: Theme Switcher & Auth */}
          <div className="flex items-center gap-2.5">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl border border-beige-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-beige-700 dark:text-slate-300 hover:text-brand-600 dark:hover:text-indigo-400 hover:bg-beige-100 dark:hover:bg-slate-800 transition-colors shadow-sm flex items-center gap-1.5 text-xs font-medium"
              title={`Switch to ${theme === 'light' ? 'Dark' : 'Beige Light'} theme`}
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <>
                  <Moon className="w-4 h-4 text-slate-700" />
                  <span className="hidden sm:inline text-xs font-semibold">Dark</span>
                </>
              ) : (
                <>
                  <Sun className="w-4 h-4 text-amber-400" />
                  <span className="hidden sm:inline text-xs font-semibold">Beige Light</span>
                </>
              )}
            </button>

            {user ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:block text-right">
                  <div className="text-xs font-semibold text-beige-900 dark:text-slate-200">{user.full_name || user.email}</div>
                  <div className="text-[10px] text-beige-600 dark:text-slate-400 capitalize">{user.role} Account</div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-xl text-beige-600 hover:text-rose-600 hover:bg-beige-100 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-slate-900 transition-colors border border-transparent hover:border-beige-200 dark:hover:border-slate-800"
                  title="Sign out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-beige-700 dark:text-slate-300 hover:text-beige-950 dark:hover:text-white hover:bg-beige-100 dark:hover:bg-slate-900 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
