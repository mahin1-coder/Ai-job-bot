import { BrowserRouter, NavLink, Route, Routes, useLocation } from "react-router-dom";
import Landing from "./components/Landing";
import ResumeUpload from "./components/ResumeUpload";
import JobBoard from "./components/JobBoard";
import ApplicationTracker from "./components/ApplicationTracker";
import AIGenerator from "./components/AIGenerator";

const NAV = [
  { to: "/resume", label: "Resume" },
  { to: "/jobs", label: "Job Board" },
  { to: "/applications", label: "Applications" },
];

function AppContent() {
  const location = useLocation();
  const isLanding = location.pathname === "/";

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Top nav - hide on landing page */}
      {!isLanding && (
        <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-8">
          <NavLink to="/" className="font-bold text-xl text-indigo-400 hover:text-indigo-300 transition">
            🤖 AI Job Bot
          </NavLink>
          <nav className="flex gap-6">
            {NAV.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `text-sm font-medium transition ${
                    isActive
                      ? "text-indigo-400 border-b-2 border-indigo-400 pb-0.5"
                      : "text-gray-400 hover:text-gray-100"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </header>
      )}

      {/* Page content */}
      <main className={!isLanding ? "max-w-6xl mx-auto px-6 py-8" : ""}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/resume" element={<ResumeUpload />} />
          <Route path="/jobs" element={<JobBoard />} />
          <Route path="/applications" element={<ApplicationTracker />} />
          <Route path="/ai/:applicationId" element={<AIGenerator />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
