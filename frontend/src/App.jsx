import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import ResumeUpload from "./components/ResumeUpload";
import JobBoard from "./components/JobBoard";
import ApplicationTracker from "./components/ApplicationTracker";
import AIGenerator from "./components/AIGenerator";

const NAV = [
  { to: "/", label: "Resume" },
  { to: "/jobs", label: "Job Board" },
  { to: "/applications", label: "Applications" },
];

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        {/* Top nav */}
        <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-8">
          <span className="font-bold text-xl text-indigo-400">🤖 AI Job Bot</span>
          <nav className="flex gap-6">
            {NAV.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end
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

        {/* Page content */}
        <main className="max-w-6xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<ResumeUpload />} />
            <Route path="/jobs" element={<JobBoard />} />
            <Route path="/applications" element={<ApplicationTracker />} />
            <Route path="/ai/:applicationId" element={<AIGenerator />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
