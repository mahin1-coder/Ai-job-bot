import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { applicationsApi, jobsApi, resumeApi } from "../services/api";

export default function JobBoard() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);  // [{job, match_score, ...}]
  const [loading, setLoading] = useState(false);
  const [matchLoading, setMatchLoading] = useState(false);
  const [resumes, setResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [mode, setMode] = useState("search"); // search | match
  const [error, setError] = useState("");

  useEffect(() => {
    resumeApi.list().then((r) => {
      setResumes(r.data);
      if (r.data.length) setSelectedResumeId(r.data[0].id);
    });
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setMatches([]);
    try {
      const { data } = await jobsApi.search({ query, location, results_per_page: 20 });
      setJobs(data);
      setMode("search");
    } catch (e) {
      setError("Search failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!query.trim() || !selectedResumeId) return;
    setMatchLoading(true);
    setError("");
    setJobs([]);
    try {
      const { data } = await jobsApi.match(selectedResumeId, {
        query,
        location,
        top_k: 10,
      });
      setMatches(data);
      setMode("match");
    } catch (e) {
      setError("Matching failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setMatchLoading(false);
    }
  };

  const handleApply = async (job) => {
    if (!selectedResumeId) return alert("Upload a resume first.");
    try {
      const { data: app } = await applicationsApi.create({
        resume_id: selectedResumeId,
        job_id: job.id,
      });
      navigate(`/ai/${app.id}`);
    } catch (e) {
      alert("Could not create application: " + (e.response?.data?.detail || e.message));
    }
  };

  const jobList = mode === "match" ? matches.map((m) => m.job) : jobs;
  const matchMap = Object.fromEntries(matches.map((m) => [m.job.id, m]));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Job Board</h1>

      {/* Search bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Job title or keywords (e.g. Python engineer)"
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-indigo-500"
        />
        <input
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Location (optional)"
          className="sm:w-48 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-indigo-500"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {loading ? "Searching…" : "Search"}
        </button>
        <button
          onClick={handleMatch}
          disabled={matchLoading || !selectedResumeId}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {matchLoading ? "Matching AI…" : "AI Match"}
        </button>
      </div>

      {/* Resume selector for matching */}
      {resumes.length > 0 && (
        <div className="flex items-center gap-3 text-sm">
          <span className="text-gray-400">Resume for AI matching:</span>
          <select
            value={selectedResumeId}
            onChange={(e) => setSelectedResumeId(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm"
          >
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.original_filename}
              </option>
            ))}
          </select>
        </div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Job listings */}
      <div className="space-y-4">
        {jobList.map((job) => {
          const matchData = matchMap[job.id];
          return (
            <div
              key={job.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-600 transition"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 flex-wrap">
                    <h3 className="font-semibold text-base">{job.title}</h3>
                    {matchData && (
                      <MatchBadge score={matchData.match_score} />
                    )}
                  </div>
                  <p className="text-sm text-gray-400 mt-0.5">
                    {job.company}
                    {job.location && ` • ${job.location}`}
                    {job.job_type && ` • ${job.job_type}`}
                  </p>
                  {job.salary_min && (
                    <p className="text-xs text-green-400 mt-1">
                      ${job.salary_min.toLocaleString()} – ${job.salary_max?.toLocaleString()}
                    </p>
                  )}
                  {matchData?.match_reasons?.length > 0 && (
                    <ul className="mt-2 space-y-0.5">
                      {matchData.match_reasons.map((r, i) => (
                        <li key={i} className="text-xs text-gray-400">• {r}</li>
                      ))}
                    </ul>
                  )}
                  {matchData?.missing_skills?.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      <span className="text-xs text-orange-400">Missing:</span>
                      {matchData.missing_skills.map((s) => (
                        <span key={s} className="px-1.5 py-0.5 bg-orange-900/30 border border-orange-700 rounded text-xs text-orange-300">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                  {job.description && (
                    <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                      {job.description}
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2 shrink-0">
                  {job.apply_url && (
                    <a
                      href={job.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1.5 border border-gray-600 hover:border-gray-400 rounded-lg text-xs font-medium"
                    >
                      View Job
                    </a>
                  )}
                  <button
                    onClick={() => handleApply(job)}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-xs font-medium"
                  >
                    Generate & Apply
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {jobList.length === 0 && !loading && !matchLoading && (
        <p className="text-center text-gray-500 py-16">
          Search for jobs or click "AI Match" to find the best fits for your resume.
        </p>
      )}
    </div>
  );
}

function MatchBadge({ score }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 75 ? "bg-green-900/40 border-green-600 text-green-300" :
    pct >= 50 ? "bg-yellow-900/40 border-yellow-600 text-yellow-300" :
    "bg-gray-800 border-gray-600 text-gray-400";
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${color}`}>
      {pct}% match
    </span>
  );
}
