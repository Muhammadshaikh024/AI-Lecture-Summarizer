export default function KeywordList({ keywords }: { keywords: string[] }) {
  return (
    <div style={{ marginTop: 16 }}>
      <h3>Keywords</h3>
      <ul>
        {keywords.map((k, i) => (
          <li key={`${k}-${i}`}>{k}</li>
        ))}
      </ul>
    </div>
  );
}