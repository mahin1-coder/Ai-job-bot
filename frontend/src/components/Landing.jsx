import { Link } from "react-router-dom";
import { useState } from "react";

export default function Landing() {
  const [demoMode, setDemoMode] = useState(false);

  const features = [
    {
      icon: "📄",
      title: "Smart Resume Parser",
      description: "AI extracts your skills, experience, and education in seconds"
    },
    {
      icon: "🔍",
      title: "Job Search",
      description: "Search 100,000+ jobs from Adzuna, RemoteOK, and more"
    },
    {
      icon: "🎯",
      title: "AI Matching",
      description: "Semantic search ranks jobs by how well they fit your background"
    },
    {
      icon: "✨",
      title: "Tailored Resumes",
      description: "Auto-generate customized resumes that match job keywords"
    },
    {
      icon: "✉️",
      title: "Cover Letters",
      description: "GPT-4 writes personalized cover letters for each application"
    },
    {
      icon: "📊",
      title: "Application Tracker",
      description: "Manage all applications in one dashboard"
    }
  ];

  const pricingPlans = [
    {
      name: "Free",
      price: "$0",
      period: "forever",
      features: [
        "5 job applications per day",
        "AI resume tailoring",
        "Cover letter generation",
        "Application tracking",
        "Basic job search"
      ],
      cta: "Get Started",
      highlighted: false
    },
    {
      name: "Pro",
      price: "$9",
      period: "/month",
      features: [
        "Unlimited applications",
        "Priority job scraping",
        "Email alerts for matches",
        "Resume templates library",
        "Export to Word/PDF",
        "LinkedIn integration (coming soon)"
      ],
      cta: "Coming Soon",
      highlighted: true
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10"></div>
        
        <div className="relative max-w-6xl mx-auto px-6 py-20 text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-indigo-500/20 rounded-full text-indigo-300 text-sm font-medium">
            🚀 Powered by GPT-4 & Semantic AI
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Stop Copy-Pasting Resumes
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto">
            AI Job Bot automatically tailors your resume and writes cover letters for every job you apply to.
          </p>
          
          <p className="text-lg text-gray-400 mb-10">
            Save 10+ hours per week. Land more interviews. Get hired faster.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/resume"
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition shadow-lg shadow-indigo-500/50"
            >
              Get Started Free
            </Link>
            
            <button
              onClick={() => setDemoMode(true)}
              className="px-8 py-4 bg-gray-800 hover:bg-gray-700 text-gray-100 font-semibold rounded-lg transition border border-gray-700"
            >
              Try Demo Mode
            </button>
          </div>

          {demoMode && (
            <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg text-green-300">
              ✅ Demo mode enabled! Sample data loaded. <Link to="/resume" className="underline">Start exploring →</Link>
            </div>
          )}

          <div className="mt-12 text-sm text-gray-500">
            ⚡ Setup in 5 minutes • 💰 ~$0.02 per application • 🔒 Your data stays private
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
          Everything You Need to <span className="text-indigo-400">Land Your Dream Job</span>
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="p-6 bg-gray-800/50 border border-gray-700 rounded-lg hover:border-indigo-500/50 transition"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-100">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-4xl mx-auto px-6 py-20">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
          How It Works
        </h2>
        
        <div className="space-y-8">
          {[
            { step: 1, title: "Upload Your Resume", desc: "PDF, Word, or text—AI extracts everything automatically" },
            { step: 2, title: "Search for Jobs", desc: "We scrape 100,000+ listings from top job boards" },
            { step: 3, title: "AI Matches & Ranks", desc: "Semantic search finds jobs that fit your background" },
            { step: 4, title: "Generate Tailored Docs", desc: "AI rewrites your resume and writes a cover letter for each job" },
            { step: 5, title: "Apply & Track", desc: "Copy, paste, apply—then track everything in your dashboard" }
          ].map(({ step, title, desc }) => (
            <div key={step} className="flex gap-6 items-start">
              <div className="flex-shrink-0 w-12 h-12 bg-indigo-600 rounded-full flex items-center justify-center text-xl font-bold">
                {step}
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-1">{title}</h3>
                <p className="text-gray-400">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pricing */}
      <div className="max-w-5xl mx-auto px-6 py-20" id="pricing">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Simple, Transparent Pricing
        </h2>
        <p className="text-center text-gray-400 mb-12">
          Start free. Upgrade when you need more.
        </p>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {pricingPlans.map((plan, idx) => (
            <div
              key={idx}
              className={`p-8 rounded-xl border-2 ${
                plan.highlighted
                  ? "border-indigo-500 bg-indigo-500/10 relative"
                  : "border-gray-700 bg-gray-800/50"
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-indigo-600 rounded-full text-sm font-semibold">
                  Coming Soon
                </div>
              )}
              
              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-gray-400">{plan.period}</span>
              </div>
              
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, fidx) => (
                  <li key={fidx} className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span className="text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <Link
                to={plan.highlighted ? "#" : "/resume"}
                className={`block w-full py-3 text-center font-semibold rounded-lg transition ${
                  plan.highlighted
                    ? "bg-indigo-600 hover:bg-indigo-700 text-white cursor-not-allowed opacity-60"
                    : "bg-gray-700 hover:bg-gray-600 text-gray-100"
                }`}
                onClick={plan.highlighted ? (e) => e.preventDefault() : undefined}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div className="p-12 bg-gradient-to-r from-indigo-600/20 to-purple-600/20 rounded-2xl border border-indigo-500/30">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Land Your Next Job?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of job seekers using AI to get hired faster.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/resume"
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition shadow-lg"
            >
              Start Free Trial
            </Link>
            
            <a
              href="https://github.com/mahin1-coder/Ai-job-bot"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-gray-800 hover:bg-gray-700 text-gray-100 font-semibold rounded-lg transition border border-gray-700"
            >
              ⭐ Star on GitHub
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-gray-400 text-sm">
          <div>
            © 2026 AI Job Bot. Built with ❤️ by developers tired of copy-pasting resumes.
          </div>
          <div className="flex gap-6">
            <a href="https://github.com/mahin1-coder/Ai-job-bot" className="hover:text-gray-100 transition">GitHub</a>
            <a href="https://github.com/mahin1-coder/Ai-job-bot/issues" className="hover:text-gray-100 transition">Issues</a>
            <a href="#pricing" className="hover:text-gray-100 transition">Pricing</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
