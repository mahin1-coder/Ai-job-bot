import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { aiApi, applicationsApi } from "../services/api";

export default function AIGenerator() {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [app, setApp] = useState(null);
  const [tab, setTab] = useState("resume"); // resume | cover_letter
  const [tone, setTone] = useState("professional");
  const [streaming, setStreaming] = useState(false);
  const [streamedText, setStreamedText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    applicationsApi.get(applicationId).then((r) => setApp(r.data));
  }, [applicationId]);

  const currentContent =
    tab === "resume" ? app?.tailored_resume : app?.cover_letter;

  // Non-streaming: generate both at once and save to DB
  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const { data } = await aiApi.generate({ application_id: applicationId, tone });
      setApp((prev) => ({
        ...prev,
        tailored_resume: data.tailored_resume,
        cover_letter: data.cover_letter,
      }));
    } catch (e) {
      alert("Generation failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setGenerating(false);
    }
  };

  // Streaming: show text in real-time via SSE
  const handleStream = () => {
    setStreaming(true);
    setStreamedText("");
    const url =
      tab === "resume"
        ? aiApi.streamResumeUrl(applicationId, tone)
        : aiApi.streamCoverLetterUrl(applicationId, tone);

    const es = new EventSource(url);
    es.onmessage = (e) => {
      if (e.data === "[DONE]") {
        es.close();
        setStreaming(false);
        // Reload app to get saved version
        applicationsApi.get(applicationId).then((r) => setApp(r.data));
        return;
      }
      setStreamedText((prev) => prev + e.data);
    };
    es.onerror = () => {
      es.close();
      setStreaming(false);
    };
  };

  const handleCopy = () => {
    const text = streaming ? streamedText : currentContent;
    if (text) {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const displayText = streaming ? streamedText : currentContent;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="text-gray-500 hover:text-white text-sm">
          ← Back
        </button>
        <h1 className="text-2xl font-bold">AI Document Generator</h1>
      </div>

      {app?.job && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 text-sm">
          <p className="font-medium">{app.job.title} — {app.job.company}</p>
          <p className="text-gray-500 mt-0.5">{app.job.location}</p>
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Tab */}
        <div className="flex rounded-lg overflow-hidden border border-gray-700 text-sm">
          {["resume", "cover_letter"].map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t); setStreamedText(""); }}
              className={`px-4 py-2 transition ${
                tab === t ? "bg-indigo-600 text-white" : "bg-gray-900 text-gray-400 hover:bg-gray-800"
              }`}
            >
              {t === "resume" ? "Tailored Resume" : "Cover Letter"}
            </button>
          ))}
        </div>

        {/* Tone */}
        <select
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="professional">Professional</option>
          <option value="enthusiastic">Enthusiastic</option>
          <option value="concise">Concise</option>
        </select>

        <button
          onClick={handleGenerate}
          disabled={generating || streaming}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {generating ? "Generating…" : "Generate Both"}
        </button>

        <button
          onClick={handleStream}
          disabled={generating || streaming}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {streaming ? "Streaming…" : "⚡ Stream"}
        </button>

        {displayText && (
          <button
            onClick={handleCopy}
            className="px-4 py-2 border border-gray-600 hover:border-gray-400 rounded-lg text-sm"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        )}
      </div>

      {/* Output */}
      {displayText ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 prose prose-invert prose-sm max-w-none overflow-auto min-h-[300px]">
          <ReactMarkdown>{displayText}</ReactMarkdown>
          {streaming && (
            <span className="inline-block w-2 h-4 bg-indigo-400 animate-pulse ml-0.5 align-middle" />
          )}
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-700 border-dashed rounded-xl p-12 text-center text-gray-500">
          <p>Click "Generate Both" or "⚡ Stream" to create your {tab === "resume" ? "tailored resume" : "cover letter"}.</p>
        </div>
      )}
    </div>
  );
}
