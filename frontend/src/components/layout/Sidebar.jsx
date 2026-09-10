import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import {
  LayoutDashboard,
  Scan,
  History,
  FileText,
  MapPin,
  Settings,
  LogOut,
  Sun,
  ShieldCheck,
  X,
} from "lucide-react";

export default function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuth();

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "New Scan", path: "/upload", icon: Scan },
    { name: "Scan History", path: "/history", icon: History },
    { name: "Reports", path: "/reports", icon: FileText },
    { name: "Solar Map", path: "/solarmap", icon: MapPin },
    { name: "Settings", path: "/settings", icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-screen w-72 bg-white border-r border-slate-200/80 flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Top Header / Brand */}
        <div>
          <div className="h-20 flex items-center justify-between px-6 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-tr from-emerald-600 to-amber-500 text-white shadow-md shadow-emerald-500/20">
                <Sun className="w-6 h-6 animate-pulse-subtle" />
                <ShieldCheck className="w-3.5 h-3.5 absolute -bottom-0.5 -right-0.5 text-emerald-100 bg-emerald-700 rounded-full p-0.5" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-xl tracking-tight text-slate-900">
                    Solar<span className="text-emerald-600">Safe</span>
                  </span>
                  <span className="text-[10px] font-semibold tracking-wider uppercase px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">
                    AI
                  </span>
                </div>
                <p className="text-xs text-slate-400 font-medium">
                  PV Fault Detection Platform
                </p>
              </div>
            </div>

            {/* Close button for mobile */}
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              aria-label="Close menu"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <div className="px-4 py-6">
            <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Navigation
            </p>
            <nav className="space-y-1.5">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => {
                      if (window.innerWidth < 1024) onClose();
                    }}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                        isActive
                          ? "bg-gradient-to-r from-emerald-600 to-emerald-500 text-white shadow-sm shadow-emerald-600/25"
                          : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Bottom User Area */}
        <div className="p-4 border-t border-slate-100">
          <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50 border border-slate-200/60 mb-2">
            <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 font-bold text-sm flex items-center justify-center shrink-0">
              {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-slate-800 truncate">
                {user?.username || "Engineer"}
              </p>
              <p className="text-xs text-slate-400 truncate">
                {user?.email || "user@solarsafe.ai"}
              </p>
            </div>
          </div>

          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sm font-medium text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-100 transition duration-150"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
