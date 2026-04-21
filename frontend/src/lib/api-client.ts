import type { UploadResponse, ProcessResponse, LectureDetail } from "./types";

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function uploadLecture(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function processLecture(lectureId: number): Promise<ProcessResponse> {
  const res = await fetch(`${API}/api/process/${lectureId}`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getLecture(lectureId: number): Promise<LectureDetail> {
  const res = await fetch(`${API}/api/lectures/${lectureId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}