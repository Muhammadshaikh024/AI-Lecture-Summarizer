export default function QuizList({ questions }: { questions: string[] }) {
  return (
    <div style={{ marginTop: 16 }}>
      <h3>Quiz Questions</h3>
      <ol>
        {questions.map((q, i) => (
          <li key={`${q}-${i}`}>{q}</li>
        ))}
      </ol>
    </div>
  );
}