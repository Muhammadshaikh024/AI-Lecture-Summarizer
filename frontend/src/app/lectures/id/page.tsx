import { getLecture } from "../../../lib/api-client";

export default async function LectureDetailPage({ params }: { params: { id: string } }) {
  const data = await getLecture(Number(params.id));

  return (
    <main>
      <h1>Lecture #{data.id}</h1>
      <p><b>Filename:</b> {data.filename}</p>

      <h3>Summary</h3>
      <p>{data.summary || "Not processed yet."}</p>

      <h3>Keywords</h3>
      <ul>{data.keywords.map((k, i) => <li key={`${k}-${i}`}>{k}</li>)}</ul>

      <h3>Questions</h3>
      <ol>{data.questions.map((q, i) => <li key={`${q}-${i}`}>{q}</li>)}</ol>
    </main>
  );
}