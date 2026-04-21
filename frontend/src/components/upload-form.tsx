"use client";

import { useState } from "react";
import { processLecture, uploadLecture } from "../lib/api-client";
import type { ProcessResponse } from "../lib/types";

export default function UploadForm({
  onDone,
}: {
  onDone: (data: ProcessResponse, lectureId: number) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!file) return alert("Please choose a file");
    setLoading(true);
    try {
      const uploaded = await uploadLecture(file);
      const processed = await processLecture(uploaded.id);
      onDone(processed, uploaded.id);
    } catch (e: any) {
      alert(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      <input type="file" accept=".pdf,.txt" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleSubmit} disabled={loading} style={{ marginLeft: 12 }}>
        {loading ? "Processing..." : "Upload & Process"}
      </button>
    </div>
  );
}