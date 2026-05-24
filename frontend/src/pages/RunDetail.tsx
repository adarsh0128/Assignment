import { Link, useParams } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { useRun } from "../hooks/useApi";

export function RunDetail() {
  const { id } = useParams();
  const { data } = useRun(id);
  if (!data) return <div>Loading run...</div>;
  return (
    <section className="rounded border bg-white p-5">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">{data.original_filename}</h1>
        <StatusBadge status={data.status} />
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-4">
        <div>Total rows: <b>{data.total_rows}</b></div>
        <div>Valid: <b>{data.valid_rows}</b></div>
        <div>Invalid: <b>{data.invalid_rows}</b></div>
        <div>Suspicious: <b>{data.suspicious_rows}</b></div>
      </div>
      <h2 className="mt-6 font-semibold">Error summary</h2>
      <pre className="mt-2 max-h-64 overflow-auto rounded bg-gray-50 p-3 text-xs">{JSON.stringify(data.error_summary, null, 2)}</pre>
      <Link className="mt-5 inline-block rounded bg-gray-900 px-4 py-2 text-white" to={`/review?run=${data.id}`}>Open review queue</Link>
    </section>
  );
}
