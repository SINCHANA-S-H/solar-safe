import { useState } from "react";
import { useAuth } from "../context/useAuth";
import { API_BASE_URL } from "../services/api";
import {
  User,
  Mail,
  Server,
  LogOut,
  Sliders,
  CheckCircle2,
} from "lucide-react";

export default function Settings() {
  const { user, logout } = useAuth();

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [highRiskAlerts, setHighRiskAlerts] = useState(true);
  const [themeMode, setThemeMode] = useState("light");
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSavePreferences = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          Account & System Settings
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Manage your Solar Safe user profile, inspection client preferences, and active runtime status
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs sm:text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Inspection client preferences updated successfully.</span>
        </div>
      )}

      {/* Profile Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-5">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-base">
            {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">Inspector Profile</h3>
            <p className="text-xs text-slate-400">Authenticated Solar Safe operator credentials</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1 mb-1">
              <User className="w-3.5 h-3.5" /> Full Name / Handle
            </span>
            <span className="text-sm font-semibold text-slate-800">
              {user?.username || "Inspector"}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1 mb-1">
              <Mail className="w-3.5 h-3.5" /> Email Address
            </span>
            <span className="text-sm font-semibold text-slate-800">
              {user?.email || "user@solarsafe.ai"}
            </span>
          </div>
        </div>
      </div>

      {/* Backend & Environment Status */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">Backend API Configuration</h3>
            <p className="text-xs text-slate-400">Target inference & database server</p>
          </div>
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">FastAPI Base URL</span>
            <span className="font-mono font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
              {API_BASE_URL}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-100">
            <span className="text-slate-500">Framework</span>
            <span className="font-semibold text-slate-800">FastAPI + Uvicorn (REST)</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-500">ML Backend Model</span>
            <span className="font-semibold text-emerald-700">MobileNetV2 (TensorFlow / Keras)</span>
          </div>
        </div>
      </div>

      {/* Client Preferences */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">Inspection Client Preferences</h3>
            <p className="text-xs text-slate-400">Local UI preferences</p>
          </div>
        </div>

        <div className="space-y-4 pt-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs sm:text-sm font-semibold text-slate-800">
                Critical Anomaly High-Risk Warnings
              </p>
              <p className="text-xs text-slate-400">
                Show immediate prominent alert banners when hotspot or crack is diagnosed
              </p>
            </div>
            <input
              type="checkbox"
              checked={highRiskAlerts}
              onChange={(e) => setHighRiskAlerts(e.target.checked)}
              className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
            />
          </div>

          <div className="flex items-center justify-between border-t border-slate-100 pt-3">
            <div>
              <p className="text-xs sm:text-sm font-semibold text-slate-800">
                Audio Notification on Prediction Completion
              </p>
              <p className="text-xs text-slate-400">
                Play subtle notification chime when model classification finishes
              </p>
            </div>
            <input
              type="checkbox"
              checked={notificationsEnabled}
              onChange={(e) => setNotificationsEnabled(e.target.checked)}
              className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
            />
          </div>

          <div className="flex items-center justify-between border-t border-slate-100 pt-3">
            <div>
              <p className="text-xs sm:text-sm font-semibold text-slate-800">Interface Theme</p>
              <p className="text-xs text-slate-400">SaaS dashboard styling surface</p>
            </div>
            <select
              value={themeMode}
              onChange={(e) => setThemeMode(e.target.value)}
              className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
            >
              <option value="light">Light Surface (Default)</option>
              <option value="dark">Dark High-Contrast (Preview)</option>
            </select>
          </div>
        </div>

        <div className="pt-2">
          <button
            onClick={handleSavePreferences}
            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition"
          >
            Save Client Preferences
          </button>
        </div>
      </div>

      {/* Security & Logout */}
      <div className="bg-white rounded-2xl border border-rose-100 shadow-xs p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Session Security</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Revoke local access token and end active inspection session
            </p>
          </div>

          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm shadow-rose-600/20 transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
}