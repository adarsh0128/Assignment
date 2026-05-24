import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { useRuns } from "../hooks/useApi";

export function Runs() {
  const { data = [] } = useRuns();
  return (
    <section>
      <h1 className="mb-4 text-lg font-semibold">Ingestion runs</h1>
      <table className="w-full bg-white text-sm">
        <thead className="bg-gray-50 text-left"><tr><th className="p-3">File</th><th>Source</th><th>Status</th><th className="text-right">Rows</th><th className="text-right">Flagged</th></tr></thead>
        <tbody>
          {data.map((run) => (
            <tr key={run.id} className="border-t">
              <td className="p-3"><Link className="text-blue-700" to={`/runs/${run.id}`}>{run.original_filename}</Link></td>
              <td>{run.source_type}</td>
              <td><StatusBadge status={run.status} /></td>
              <td className="text-right">{run.total_rows}</td>
              <td className="text-right pr-3">{run.suspicious_rows}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
