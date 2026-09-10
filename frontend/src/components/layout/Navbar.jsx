import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { Menu, Plus, User as UserIcon } from "lucide-react";
import api, { API_BASE_URL } from "../../services/api";

export default function Navbar({ onOpenSidebar }) {
  const { user } = useAuth();
  const location = useLocation();
  const [isBackendOnline, setIsBackendOnline] = useState(null);

  // Determine current page title
  const getPageTitle = () => {
    switch (location.pathname) {
      case "/dashboard":
        return "Dashboard Overview";
      case "/upload":
        return "AI Solar PV Inspection";
      case "/history":
        return "Scan History";
      case "/reports":
        return "Generated Reports";
      case "/solarmap":
        return "Solar Geospatial Map";
      case "/settings":
        return "Account & System Settings";
      default:
        return "Solar Safe Platform";
    }
  };

  // Heartbeat check to verify backend health
  useEffect(() => {
    let isMounted = true;
    const checkBackend = async () => {
      try {
        await api.get("/", { timeout: 4000 });
        if (isMounted) setIsBackendOnline(true);
      } catch {
        if (isMounted) setIsBackendOnline(false);
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 h-20 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-8 flex items-center justify-between">
      <div className="flex items-center gap-4">
        {/* Mobile toggle */}
        <button
          onClick={onOpenSidebar}
          className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
          aria-label="Open sidebar"
        >
          <Menu className="w-6 h-6" />
        </button>

        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            {getPageTitle()}
          </h1>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-xs text-slate-400 font-medium">SolarSafe v1.0</span>
            <span className="text-slate-300">•</span>
            <div className="flex items-center gap-1.5" title={`API Target: ${API_BASE_URL}`}>
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendOnline === true
                    ? "bg-emerald-500 shadow-xs shadow-emerald-500/50 animate-pulse"
                    : isBackendOnline === false
                    ? "bg-rose-500"
                    : "bg-amber-400"
                }`}
              />
              <span className="text-[11px] font-medium text-slate-500">
                {isBackendOnline === true
                  ? "FastAPI ML Ready"
                  : isBackendOnline === false
                  ? "Backend Offline"
                  : "Checking Backend..."}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Quick New Scan CTA */}
        {location.pathname !== "/upload" && (
          <Link
            to="/upload"
            className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm shadow-sm shadow-emerald-600/25 transition active:scale-98"
          >
            <Plus className="w-4 h-4" />
            <span>Analyze Panel</span>
          </Link>
        )}

        {/* User indicator */}
        <Link
          to="/settings"
          className="flex items-center gap-2.5 p-1.5 sm:px-3 sm:py-2 rounded-xl border border-slate-200/80 hover:bg-slate-50 transition"
          title="Go to Settings"
        >
          <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
            {user?.username ? user.username.charAt(0).toUpperCase() : <UserIcon className="w-4 h-4" />}
          </div>
          <span className="hidden md:inline text-sm font-semibold text-slate-700">
            {user?.username || "Account"}
          </span>
        </Link>
      </div>
    </header>
  );
}
