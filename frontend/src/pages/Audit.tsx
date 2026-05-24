import { useParams } from "react-router-dom";
import { useAudit } from "../hooks/useApi";

export function Audit() {
  const { recordId } = useParams();
  const { data = [] } = useAudit(recordId);
  return (
    <section className="rounded border bg-white p-5">
      <h1 className="text-lg font-semibold">Audit timeline for record {recordId}</h1>
      <div className="mt-5 space-y-4">
        {data.map((item) => (
          <div key={item.id} className="rounded border p-3">
            <div className="font-medium">{item.field_name}</div>
            <div className="text-sm text-gray-700">{JSON.stringify(item.old_value)} {"->"} {JSON.stringify(item.new_value)}</div>
            <div className="mt-1 text-xs text-gray-500">{item.actor_username} at {new Date(item.created_at).toLocaleString()}</div>
            {item.reason && <div className="mt-2 text-sm">{item.reason}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}
