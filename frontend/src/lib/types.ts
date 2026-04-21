export type UploadResponse = {
  id: number;
  filename: string;
  raw_text_preview: string;
};

export type ProcessResponse = {
  lecture_id: number;
  summary: string;
  keywords: string[];
  questions: string[];
};

export type LectureDetail = {
  id: number;
  filename: string;
  summary?: string | null;
  keywords: string[];
  questions: string[];
};