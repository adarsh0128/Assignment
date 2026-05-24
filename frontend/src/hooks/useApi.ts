import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import type { AuditLog, Dashboard, DataSource, IngestionRun, NormalizedRecord, Paginated } from "../api/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get<Dashboard>("/dashboard/")).data
  });
}

export function useDataSources() {
  return useQuery({
    queryKey: ["data-sources"],
    queryFn: async () => (await api.get<Paginated<DataSource>>("/data-sources/")).data.results
  });
}

export function useRuns() {
  return useQuery({
    queryKey: ["runs"],
    queryFn: async () => (await api.get<Paginated<IngestionRun>>("/runs/")).data.results
  });
}

export function useRun(id: string | undefined) {
  return useQuery({
    queryKey: ["run", id],
    enabled: Boolean(id),
    queryFn: async () => (await api.get<IngestionRun>(`/runs/${id}/`)).data
  });
}

export function useReviewRecords(filters: Record<string, string>) {
  return useQuery({
    queryKey: ["records", filters],
    queryFn: async () => (await api.get<Paginated<NormalizedRecord>>("/normalized-records/", { params: filters })).data.results
  });
}

export function useRecord(id: string | undefined) {
  return useQuery({
    queryKey: ["record", id],
    enabled: Boolean(id),
    queryFn: async () => (await api.get<NormalizedRecord>(`/normalized-records/${id}/`)).data
  });
}

export function useAudit(recordId: string | undefined) {
  return useQuery({
    queryKey: ["audit", recordId],
    enabled: Boolean(recordId),
    queryFn: async () => (await api.get<Paginated<AuditLog>>(`/audit/${recordId}/`)).data.results
  });
}

export function useReviewAction(recordId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { action: string; reason?: string }) =>
      (await api.post(`/review/${recordId}/action/`, payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
      queryClient.invalidateQueries({ queryKey: ["record", recordId] });
      queryClient.invalidateQueries({ queryKey: ["audit", recordId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    }
  });
}

export function useBulkApprove() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (recordIds: number[]) =>
      (await api.post("/review/bulk-approve/", { record_ids: recordIds, reason: "Bulk approved from review queue" })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["records"] })
  });
}
