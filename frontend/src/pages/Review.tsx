import { Link } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { useBulkApprove, useReviewRecords } from "../hooks/useApi";
import { useState } from "react";

export function Review() {
  const [filters, setFilters] = useState({ status: "", source_type: "", is_suspicious: "" });
  const queryFilters = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
  const { data = [] } = useReviewRecords(queryFilters);
  const [selected, setSelected] = useState<number[]>([]);
  const bulkApprove = useBulkApprove();

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <select className="rounded border px-3 py-2" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All statuses</option>
          {["pending", "flagged", "approved", "rejected", "locked"].map((status) => <option key={status}>{status}</option>)}
        </select>
        <select className="rounded border px-3 py-2" value={filters.source_type} onChange={(e) => setFilters({ ...filters, source_type: e.target.value })}>
          <option value="">All sources</option>
          {["sap", "utility", "travel"].map((source) => <option key={source}>{source}</option>)}
        </select>
        <select className="rounded border px-3 py-2" value={filters.is_suspicious} onChange={(e) => setFilters({ ...filters, is_suspicious: e.target.value })}>
          <option value="">Any suspicion</option>
          <option value="true">Suspicious</option>
          <option value="false">Not suspicious</option>
        </select>
        <button className="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-40" disabled={!selected.length} onClick={() => bulkApprove.mutate(selected)}>Bulk approve</button>
      </div>
      <table className="w-full bg-white text-sm">
        <thead className="bg-gray-50 text-left"><tr><th className="p-3"></th><th>Record</th><th>Source</th><th>Status</th><th>Quantity</th><th>Suspicion</th><th></th></tr></thead>
        <tbody>
          {data.map((record) => (
            <tr key={record.id} className={`border-t ${record.is_suspicious ? "bg-amber-50" : ""}`}>
              <td className="p-3"><input type="checkbox" checked={selected.includes(record.id)} onChange={(e) => setSelected(e.target.checked ? [...selected, record.id] : selected.filter((id) => id !== record.id))} /></td>
              <td><Link className="text-blue-700" to={`/review/${record.id}`}>{record.source_reference || record.id}</Link></td>
              <td>{record.source_type}</td>
              <td><StatusBadge status={record.status} /></td>
              <td>{record.canonical_quantity} {record.canonical_unit}</td>
              <td>{record.suspicion_reasons.join("; ")}</td>
              <td className="pr-3 text-right"><Link className="text-blue-700" to={`/audit/${record.id}`}>View audit</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
