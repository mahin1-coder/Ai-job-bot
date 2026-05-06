import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { resumeApi } from "../services/api";

export default function ResumeUpload() {
  const [resumes, setResumes] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  // Load existing resumes on mount
  useEffect(() => {
    resumeApi.list().then((r) => setResumes(r.data));
  }, []);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles.length) return;
    const file = acceptedFiles[0];
    setUploading(true);
    setError("");
    try {
      const { data } = await resumeApi.upload(file);
      setResumes((prev) => [data, ...prev]);
      setSelected(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
  });

  const handleDelete = async (id) => {
    await resumeApi.delete(id);
    setResumes((prev) => prev.filter((r) => r.id !== id));
    if (selected?.id === id) setSelected(null);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">My Resumes</h1>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
          isDragActive
            ? "border-indigo-500 bg-indigo-950/30"
            : "border-gray-700 hover:border-indigo-500/60"
        }`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <p className="text-indigo-400 animate-pulse">Uploading & parsing with AI…</p>
        ) : (
          <>
            <p className="text-gray-300 text-lg">
              {isDragActive ? "Drop it here!" : "Drag & drop your resume here"}
            </p>
            <p className="text-gray-500 text-sm mt-1">PDF, DOCX, or TXT • Max 10MB</p>
            <button className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium">
              Browse file
            </button>
          </>
        )}
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Resume list */}
      {resumes.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-300">Uploaded Resumes</h2>
          {resumes.map((r) => (
            <div
              key={r.id}
              onClick={() => setSelected(r)}
              className={`flex items-center justify-between px-5 py-4 rounded-xl border cursor-pointer transition ${
                selected?.id === r.id
                  ? "border-indigo-500 bg-indigo-950/30"
                  : "border-gray-800 bg-gray-900 hover:border-gray-600"
              }`}
            >
              <div>
                <p className="font-medium text-sm">{r.original_filename}</p>
                <p className="text-xs text-gray-500 mt-0.5">
                  {new Date(r.created_at).toLocaleDateString()} • {r.file_type.toUpperCase()}
                </p>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); handleDelete(r.id); }}
                className="text-gray-600 hover:text-red-400 text-xs px-2 py-1 rounded"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Parsed data preview */}
      {selected?.parsed_data && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
          <h2 className="font-bold text-lg text-indigo-300">
            Parsed: {selected.parsed_data.name || "Resume"}
          </h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500 mb-1">Email</p>
              <p>{selected.parsed_data.email || "—"}</p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">Phone</p>
              <p>{selected.parsed_data.phone || "—"}</p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">Location</p>
              <p>{selected.parsed_data.location || "—"}</p>
            </div>
          </div>
          {selected.parsed_data.skills?.length > 0 && (
            <div>
              <p className="text-gray-500 text-sm mb-2">Skills</p>
              <div className="flex flex-wrap gap-2">
                {selected.parsed_data.skills.map((s) => (
                  <span key={s} className="px-2 py-0.5 bg-indigo-900/50 border border-indigo-700 rounded text-xs text-indigo-300">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}
          {selected.parsed_data.summary && (
            <div>
              <p className="text-gray-500 text-sm mb-1">Summary</p>
              <p className="text-sm text-gray-300 leading-relaxed">
                {selected.parsed_data.summary}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
