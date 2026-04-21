export default function SummaryCard({ summary }: { summary: string }) {
  return (
    <div style={{ marginTop: 16 }}>
      <h3>Summary</h3>
      <p>{summary}</p>
    </div>
  );
}