import { FormEvent, useState } from "react";
import { UploadCloud } from "lucide-react";
import { api } from "../api/client";
import { useDataSources } from "../hooks/useApi";

export function Upload() {
  const { data: sources = [] } = useDataSources();
  const [dataSource, setDataSource] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>("");
  const [progress, setProgress] = useState(0);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!file || !dataSource) return;
    const body = new FormData();
    body.append("data_source", dataSource);
    body.append("file", file);
    const response = await api.post("/uploads/", body, {
      onUploadProgress: (evt) => setProgress(evt.total ? Math.round((evt.loaded / evt.total) * 100) : 0)
    });
    setResult(`Run ${response.data.id}: ${response.data.status}, ${response.data.invalid_rows} invalid rows, ${response.data.suspicious_rows} suspicious rows.`);
  }

  return (
    <form onSubmit={submit} className="max-w-2xl rounded border bg-white p-5">
      <h1 className="mb-4 text-lg font-semibold">Upload source file</h1>
      <select className="mb-4 w-full rounded border px-3 py-2" value={dataSource} onChange={(e) => setDataSource(e.target.value)}>
        <option value="">Select source</option>
        {sources.map((source) => <option key={source.id} value={source.id}>{source.name} ({source.source_type})</option>)}
      </select>
      <label className="flex cursor-pointer flex-col items-center rounded border border-dashed p-8 text-center">
        <UploadCloud className="mb-2 h-8 w-8 text-gray-500" />
        <span className="text-sm text-gray-600">{file ? file.name : "Drop or select CSV"}</span>
        <input className="hidden" type="file" accept=".csv,text/csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      </label>
      {progress > 0 && <div className="mt-4 h-2 rounded bg-gray-100"><div className="h-2 rounded bg-gray-900" style={{ width: `${progress}%` }} /></div>}
      <button className="mt-4 rounded bg-gray-900 px-4 py-2 text-white">Upload</button>
      {result && <div className="mt-4 rounded bg-amber-50 px-3 py-2 text-sm text-amber-900">{result}</div>}
    </form>
  );
}
