import { NavLink, Outlet } from "react-router-dom";

const links = [
  ["/dashboard", "Dashboard"],
  ["/upload", "Upload"],
  ["/runs", "Runs"],
  ["/review", "Review"]
];

export function Layout() {
  return (
    <div className="min-h-screen">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <div className="text-lg font-semibold">ESG Audit Platform</div>
            <div className="text-xs text-gray-500">Enterprise ingestion and analyst review</div>
          </div>
          <nav className="flex gap-2">
            {links.map(([to, label]) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `rounded px-3 py-2 text-sm ${isActive ? "bg-gray-900 text-white" : "text-gray-600 hover:bg-gray-100"}`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-6">
        <Outlet />
      </main>
    </div>
  );
}
