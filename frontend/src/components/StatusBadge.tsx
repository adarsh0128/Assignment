import type { RecordStatus } from "../api/types";

const classes: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700",
  flagged: "bg-amber-100 text-amber-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  locked: "bg-purple-100 text-purple-800",
  completed: "bg-green-100 text-green-800",
  completed_with_errors: "bg-amber-100 text-amber-800",
  failed: "bg-red-100 text-red-800",
  processing: "bg-blue-100 text-blue-800",
  received: "bg-gray-100 text-gray-700"
};

export function StatusBadge({ status }: { status: RecordStatus | string }) {
  return <span className={`rounded px-2 py-1 text-xs font-medium ${classes[status] ?? classes.pending}`}>{status}</span>;
}
