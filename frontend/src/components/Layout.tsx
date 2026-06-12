import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/incidents", label: "Incidents" },
  { to: "/insights", label: "Insights" },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-lg font-semibold text-white">FCI Platform</h1>
            <p className="text-xs text-slate-400">Failure Capture & Intelligence</p>
          </div>
          <nav className="flex gap-4">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-sm ${
                  location.pathname === link.to || (link.to !== "/" && location.pathname.startsWith(link.to))
                    ? "text-cyan-400"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  );
}
