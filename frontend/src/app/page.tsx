"use client";

import { useState } from "react";

type ProcessResponse = {
  lecture_id: number;
  summary: string;
  keywords: string[];
  questions: string[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [lectureId, setLectureId] = useState<number | null>(null);

  const [summary, setSummary] = useState("");
  const [keywords, setKeywords] = useState<string[]>([]);
  const [questions, setQuestions] = useState<string[]>([]);

  const resetResult = () => {
    setLectureId(null);
    setSummary("");
    setKeywords([]);
    setQuestions([]);
  };

  const handleProcess = async () => {
    if (!file) return;

    setLoading(true);
    setError("");
    setStatus("Uploading file...");
    resetResult();

    try {
      // 1) Upload
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const t = await uploadRes.text();
        throw new Error(`Upload failed (${uploadRes.status}): ${t}`);
      }

      const uploadData = await uploadRes.json();
      const id = uploadData?.lecture_id;
      if (!id) throw new Error("Upload succeeded but lecture_id missing.");

      setLectureId(id);

      // 2) Process
      setStatus("Processing lecture...");
      const processRes = await fetch(`${API_BASE}/api/process/${id}`, {
        method: "POST",
      });

      if (!processRes.ok) {
        const t = await processRes.text();
        throw new Error(`Process failed (${processRes.status}): ${t}`);
      }

      const data: ProcessResponse = await processRes.json();

      setSummary(data.summary || "");
      setKeywords(data.keywords || []);
      setQuestions(data.questions || []);
      setStatus("Done ✅");
    } catch (e: any) {
      setError(e?.message || "Something went wrong");
      setStatus("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <h1 className="title">AI Lecture Summarizer</h1>
      <p className="subtitle">
        Upload a lecture PDF/TXT, get summary, keywords, and quiz questions.
      </p>

      <section className="panel">
        <div className="uploadRow">
          <input
            className="inputFile"
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />

          <button className="btn" onClick={handleProcess} disabled={!file || loading}>
            {loading ? "Processing..." : "Generate"}
          </button>
        </div>

        {file && (
          <div className="status">
            Selected: <b>{file.name}</b>
          </div>
        )}
        {lectureId && <div className="status ok">Saved Lecture ID: {lectureId}</div>}
        {status && <div className="status ok">{status}</div>}
        {error && <div className="status err">{error}</div>}
      </section>

      <section className="grid">
        <article className="card summary">
          <h3>Summary</h3>
          <pre className="textBlock">{summary || "No summary yet."}</pre>
        </article>

        <article className="card keywords">
          <h3>Keywords</h3>
          <div className="pillWrap">
            {keywords.length ? (
              keywords.map((k, i) => (
                <span className="pill" key={i}>
                  {k}
                </span>
              ))
            ) : (
              <span className="muted">No keywords yet.</span>
            )}
          </div>
        </article>

        <article className="card quiz">
          <h3>Quiz Questions</h3>
          {questions.length ? (
            <ol className="list">
              {questions.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ol>
          ) : (
            <p className="muted">No questions yet.</p>
          )}
        </article>
      </section>
    </main>
  );
}