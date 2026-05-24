import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { useDashboard } from "../hooks/useApi";

export function Dashboard() {
  const { data, isLoading } = useDashboard();
  if (isLoading) return <div>Loading dashboard...</div>;
  if (!data) return <div>No dashboard data returned.</div>;
  const cards = [
    ["Total runs", data.total_runs],
    ["Pending reviews", data.pending_reviews],
    ["Flagged rows", data.flagged_rows],
    ["Approved this week", data.approved_this_week]
  ];
  return (
    <section>
      <div className="grid gap-4 md:grid-cols-4">
        {cards.map(([label, value]) => (
          <div key={label} className="rounded border bg-white p-4">
            <div className="text-sm text-gray-500">{label}</div>
            <div className="mt-2 text-2xl font-semibold">{value}</div>
          </div>
        ))}
      </div>
      <h2 className="mt-8 text-lg font-semibold">Recent ingestion runs</h2>
      <table className="mt-3 w-full border-collapse bg-white text-sm">
        <tbody>
          {data.recent_runs.map((run) => (
            <tr key={run.id} className="border-b">
              <td className="p-3"><Link className="font-medium text-blue-700" to={`/runs/${run.id}`}>{run.original_filename}</Link></td>
              <td className="p-3">{run.source_type}</td>
              <td className="p-3"><StatusBadge status={run.status} /></td>
              <td className="p-3 text-right">{run.suspicious_rows} flagged</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
