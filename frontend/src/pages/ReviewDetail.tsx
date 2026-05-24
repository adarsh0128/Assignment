import { useParams } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { useAudit, useRecord, useReviewAction } from "../hooks/useApi";
import type { RecordStatus } from "../api/types";

const allowedActions: Record<RecordStatus, string[]> = {
  pending: ["flag", "approve"],
  flagged: ["approve", "reject"],
  approved: ["lock"],
  rejected: ["reopen"],
  locked: []
};

export function ReviewDetail() {
  const { id } = useParams();
  const { data } = useRecord(id);
  const { data: audit = [] } = useAudit(id);
  const action = useReviewAction(id);
  if (!data) return <div>Loading record...</div>;
  const actions = allowedActions[data.status];
  return (
    <section className="grid gap-5 lg:grid-cols-[1fr_360px]">
      <div className="rounded border bg-white p-5">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold">Record {data.id}</h1>
          <StatusBadge status={data.status} />
        </div>
        {data.is_suspicious && <div className="mt-4 rounded bg-amber-50 px-3 py-2 text-sm text-amber-900">{data.suspicion_reasons.join("; ")}</div>}
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <pre className="overflow-auto rounded bg-gray-50 p-3 text-xs">{JSON.stringify(data.raw_payload, null, 2)}</pre>
          <pre className="overflow-auto rounded bg-gray-50 p-3 text-xs">{JSON.stringify(data.normalized_payload, null, 2)}</pre>
        </div>
      </div>
      <aside className="rounded border bg-white p-5">
        <h2 className="font-semibold">Approval</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {actions.map((name) => (
            <button
              key={name}
              className="rounded border px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
              disabled={action.isPending}
              onClick={() => action.mutate({ action: name, reason: "Analyst decision" })}
            >
              {action.isPending ? "Saving..." : name}
            </button>
          ))}
        </div>
        {!actions.length && <div className="mt-3 rounded bg-gray-50 px-3 py-2 text-sm text-gray-600">Locked records have no available actions.</div>}
        <h2 className="mt-6 font-semibold">Audit timeline</h2>
        <div className="mt-3 space-y-3 text-sm">
          {audit.map((item) => (
            <div key={item.id} className="border-l-2 border-gray-300 pl-3">
              <div className="font-medium">{item.field_name}: {String(item.old_value)} {"->"} {String(item.new_value)}</div>
              <div className="text-xs text-gray-500">{item.actor_username} at {new Date(item.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </aside>
    </section>
  );
}
