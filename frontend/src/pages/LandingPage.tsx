import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Upload, ArrowRight, Lock, Cpu, FileCheck } from 'lucide-react';
import { RiskBadge } from '../components/RiskBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-16 py-8">
      <DisclaimerBanner />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8 pt-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 dark:bg-indigo-500/10 dark:border-indigo-500/20 dark:text-indigo-400 text-xs font-bold tracking-wide">
          <Cpu className="w-3.5 h-3.5" />
          <span>Local Legal-BERT & Rule-Based Intelligence</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-beige-950 dark:text-white max-w-4xl mx-auto leading-tight sm:leading-tight">
          Understand your contract <br className="hidden sm:inline" />
          <span className="text-brand-600 dark:text-brand-400">
            before you sign it.
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-base sm:text-lg text-beige-700 dark:text-slate-300 leading-relaxed">
          Upload any English PDF or DOCX agreement. Automatically segment clauses, classify obligations, detect predatory terms, and generate plain-English explanations.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link
            to="/upload"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5"
          >
            <span>Analyze a Contract</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/register"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold bg-white dark:bg-slate-800/80 hover:bg-beige-100 dark:hover:bg-slate-700 text-beige-800 dark:text-slate-200 border border-beige-200 dark:border-slate-700/60 shadow-sm transition-all"
          >
            Create Free Account
          </Link>
        </div>

        {/* Local Processing Privacy Badge */}
        <div className="pt-4 flex items-center justify-center gap-6 text-xs text-beige-600 dark:text-slate-400">
          <div className="flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span className="font-medium">Zero Third-Party Cloud APIs</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-brand-600 dark:text-indigo-400" />
            <span className="font-medium">100% Local Inference & Storage</span>
          </div>
        </div>
      </section>

      {/* 3-Step Workflow */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-y border-beige-200 dark:border-slate-800/60 bg-beige-100/50 dark:bg-slate-900/30">
        <div className="text-center space-y-2 mb-12">
          <h2 className="text-xs uppercase font-bold tracking-widest text-brand-700 dark:text-indigo-400">How It Works</h2>
          <p className="text-2xl sm:text-3xl font-extrabold text-beige-950 dark:text-white">Three steps to contractual clarity</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-panel p-6 rounded-2xl space-y-4 relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-brand-50 border border-brand-200 dark:bg-indigo-500/10 dark:border-indigo-500/20 flex items-center justify-center text-brand-700 dark:text-indigo-400 font-extrabold text-lg">
              1
            </div>
            <h3 className="text-lg font-bold text-beige-950 dark:text-white flex items-center gap-2">
              <Upload className="w-5 h-5 text-brand-600 dark:text-indigo-400" />
              Upload Agreement
            </h3>
            <p className="text-sm text-beige-600 dark:text-slate-400 leading-relaxed">
              Drag and drop any standard PDF or DOCX agreement. The parser normalizes text, strips headers, and breaks it into clauses.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl space-y-4 relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-purple-50 border border-purple-200 dark:bg-purple-500/10 dark:border-purple-500/20 flex items-center justify-center text-purple-700 dark:text-purple-400 font-extrabold text-lg">
              2
            </div>
            <h3 className="text-lg font-bold text-beige-950 dark:text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              Analyze & Extract
            </h3>
            <p className="text-sm text-beige-600 dark:text-slate-400 leading-relaxed">
              Classifies each clause into 8 canonical categories, extracts numeric thresholds, and applies explainable risk rules.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl space-y-4 relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 dark:bg-emerald-500/10 dark:border-emerald-500/20 flex items-center justify-center text-emerald-700 dark:text-emerald-400 font-extrabold text-lg">
              3
            </div>
            <h3 className="text-lg font-bold text-beige-950 dark:text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              Understand & Act
            </h3>
            <p className="text-sm text-beige-600 dark:text-slate-400 leading-relaxed">
              Review flagged high-risk clauses in an interactive viewer, read plain-English mitigation advice, and export PDF reports.
            </p>
          </div>
        </div>
      </section>

      {/* Interactive Example Risk Cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-xs uppercase font-bold tracking-widest text-brand-700 dark:text-indigo-400">Explainable Intelligence</h2>
          <p className="text-2xl sm:text-3xl font-extrabold text-beige-950 dark:text-white">Sample Flagged Clause Scenarios</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card 1: High Risk */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/80 border border-rose-200 dark:border-rose-500/30 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <CategoryBadge category="Termination" />
              <RiskBadge level="High" score={75} showScore />
            </div>

            <div className="text-xs font-mono bg-beige-50 dark:bg-slate-950 p-3 rounded-xl border border-beige-200 dark:border-slate-800 text-beige-900 dark:text-slate-300">
              "Company reserves the sole discretion to terminate this Agreement immediately without prior notice."
            </div>

            <div className="space-y-1 text-xs text-beige-800 dark:text-slate-300">
              <span className="font-bold text-rose-700 dark:text-rose-300">Plain-English Analysis:</span>
              <p className="text-beige-600 dark:text-slate-400">
                This clause gives one party unilateral power to end the agreement without giving you time to transition or prepare.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 dark:bg-rose-950/20 dark:border-rose-500/20 dark:text-rose-200 font-medium">
              <strong>Recommendation:</strong> Request bilateral termination rights with at least 30 days prior written notice.
            </div>
          </div>

          {/* Card 2: Low Risk / Balanced */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/80 border border-emerald-200 dark:border-emerald-500/30 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <CategoryBadge category="Limitation of Liability" />
              <RiskBadge level="Low" score={10} showScore />
            </div>

            <div className="text-xs font-mono bg-beige-50 dark:bg-slate-950 p-3 rounded-xl border border-beige-200 dark:border-slate-800 text-beige-900 dark:text-slate-300">
              "Each party's aggregate liability shall be mutually capped at the total fees paid in the preceding twelve (12) months."
            </div>

            <div className="space-y-1 text-xs text-beige-800 dark:text-slate-300">
              <span className="font-bold text-emerald-700 dark:text-emerald-300">Plain-English Analysis:</span>
              <p className="text-beige-600 dark:text-slate-400">
                This clause is balanced. Both parties face the exact same reciprocal cap equal to one year of service fees.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 dark:bg-emerald-950/20 dark:border-emerald-500/20 dark:text-emerald-200 font-medium">
              <strong>Recommendation:</strong> Clause complies with standard bilateral commercial contracting norms.
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center pb-6">
        <div className="p-10 rounded-3xl bg-beige-100/80 dark:bg-slate-900 border border-beige-200 dark:border-slate-800 space-y-6 shadow-sm">
          <h2 className="text-3xl font-extrabold text-beige-950 dark:text-white">Ready to audit your contracts?</h2>
          <p className="text-beige-700 dark:text-slate-300 max-w-xl mx-auto text-sm sm:text-base">
            Never sign an agreement with hidden traps, perpetual liabilities, or unilateral cancellation terms again.
          </p>
          <div>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-sm transition-all"
            >
              <span>Get Started Now</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
