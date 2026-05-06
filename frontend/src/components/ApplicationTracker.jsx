import { useEffect, useState } from "react";
import { applicationsApi } from "../services/api";
import { useNavigate } from "react-router-dom";

const STATUS_COLORS = {
  pending: "bg-gray-700 text-gray-300",
  applying: "bg-blue-900/40 text-blue-300 border-blue-700",
  applied: "bg-indigo-900/40 text-indigo-300 border-indigo-700",
  interviewing: "bg-yellow-900/40 text-yellow-300 border-yellow-700",
  offer: "bg-green-900/40 text-green-300 border-green-700",
  rejected: "bg-red-900/40 text-red-300 border-red-700",
  withdrawn: "bg-gray-800 text-gray-500 border-gray-700",
};

const ALL_STATUSES = ["pending", "applying", "applied", "interviewing", "offer", "rejected", "withdrawn"];

export default function ApplicationTracker() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const [appsRes, statsRes] = await Promise.all([
      applicationsApi.list(),
      applicationsApi.stats(),
    ]);
    setApplications(appsRes.data);
    setStats(statsRes.data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleStatusChange = async (id, newStatus) => {
    await applicationsApi.updateStatus(id, { status: newStatus });
    setApplications((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: newStatus } : a))
    );
  };

  const handleDelete = async (id) => {
    await applicationsApi.delete(id);
    setApplications((prev) => prev.filter((a) => a.id !== id));
  };

  if (loading) return <p className="text-gray-500 py-16 text-center">Loading…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Application Tracker</h1>

      {/* Stats row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Total" value={stats.total} color="text-white" />
          <StatCard label="Applied" value={stats.by_status?.applied || 0} color="text-indigo-300" />
          <StatCard label="Interviewing" value={stats.by_status?.interviewing || 0} color="text-yellow-300" />
          <StatCard label="Offers" value={stats.by_status?.offer || 0} color="text-green-300" />
        </div>
      )}

      {/* Applications table */}
      {applications.length === 0 ? (
        <p className="text-center text-gray-500 py-16">
          No applications yet. Go to the Job Board and click "Generate & Apply".
        </p>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <div
              key={app.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">
                  {app.job?.title || "Job"} — {app.job?.company || ""}
                </p>
                <p className="text-xs text-gray-500 mt-0.5">
                  {app.job?.location || ""}
                  {app.match_score != null && (
                    <> • <span className="text-indigo-400">{Math.round(app.match_score * 100)}% match</span></>
                  )}
                  {app.applied_at && <> • Applied {new Date(app.applied_at).toLocaleDateString()}</>}
                </p>
                {app.notes && (
                  <p className="text-xs text-gray-400 mt-1 italic">{app.notes}</p>
                )}
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {/* Status dropdown */}
                <select
                  value={app.status}
                  onChange={(e) => handleStatusChange(app.id, e.target.value)}
                  className={`text-xs px-2 py-1 rounded-lg border bg-transparent ${STATUS_COLORS[app.status] || "text-gray-300"}`}
                >
                  {ALL_STATUSES.map((s) => (
                    <option key={s} value={s} className="bg-gray-900 text-white">
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </option>
                  ))}
                </select>

                {/* AI artifacts button */}
                {(app.tailored_resume || app.cover_letter) && (
                  <button
                    onClick={() => navigate(`/ai/${app.id}`)}
                    className="text-xs px-3 py-1.5 bg-indigo-900/40 border border-indigo-700 rounded-lg text-indigo-300 hover:bg-indigo-900/70"
                  >
                    View AI Docs
                  </button>
                )}

                {/* Generate button if not generated */}
                {!app.tailored_resume && (
                  <button
                    onClick={() => navigate(`/ai/${app.id}`)}
                    className="text-xs px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-medium"
                  >
                    Generate
                  </button>
                )}

                <button
                  onClick={() => handleDelete(app.id)}
                  className="text-xs text-gray-600 hover:text-red-400 px-2"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
