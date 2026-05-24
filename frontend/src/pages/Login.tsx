import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { setTokens } from "../api/auth";

export function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const response = await api.post<{ access: string; refresh: string }>("/auth/token/", { username, password });
      setTokens(response.data.access, response.data.refresh);
      navigate("/dashboard");
    } catch {
      setError("Invalid credentials or unavailable API.");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 px-4">
      <form onSubmit={submit} className="w-full max-w-sm rounded border bg-white p-6 shadow-sm">
        <h1 className="mb-5 text-xl font-semibold">Sign in</h1>
        <label className="mb-3 block text-sm">
          <span className="mb-1 block text-gray-600">Username</span>
          <input className="w-full rounded border px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label className="mb-4 block text-sm">
          <span className="mb-1 block text-gray-600">Password</span>
          <input className="w-full rounded border px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <div className="mb-3 rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <button className="w-full rounded bg-gray-900 px-4 py-2 text-white">Sign in</button>
      </form>
    </div>
  );
}
