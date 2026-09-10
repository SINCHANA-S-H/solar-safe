import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import historyService from "../services/historyService";
import reportService from "../services/reportService";
import DashboardCards from "../components/dashboard/DashboardCards";
import {
  Plus,
  FileDown,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Flame,
  CheckCircle2,
  RefreshCw,
  Sparkles,
  Inbox,
  Loader2,
} from "lucide-react";

export default function Dashboard() {
  const { user } = useAuth();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    if (!user?.email) return;
    let isMounted = true;

    historyService
      .getHistory(user.email)
      .then((data) => {
        if (isMounted) {
          setScans(Array.isArray(data) ? data : []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to load scan records from backend.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [user?.email]);

  const handleManualRefresh = async () => {
    if (!user?.email) return;
    setLoading(true);
    setError(null);
    try {
      const data = await historyService.getHistory(user.email);
      setScans(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load scan records from backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async (scan) => {
    setDownloadingId(scan.id);
    try {
      const blob = await reportService.generateReport(
        user.email,
        scan.prediction,
        scan.confidence
      );
      reportService.downloadPdfBlob(blob, `Report_Scan_${scan.id}_${scan.prediction}.pdf`);
    } catch (err) {
      alert(`Could not generate report: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const getConditionBadge = (prediction) => {
    switch (prediction) {
      case "Normal":
        return {
          label: "Normal",
          badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
          icon: CheckCircle2,
        };
      case "Hotspot":
        return {
          label: "Hotspot",
          badge: "bg-amber-50 text-amber-700 border-amber-200",
          icon: Flame,
        };
      case "Cell_Crack":
        return {
          label: "Cell Crack",
          badge: "bg-rose-50 text-rose-700 border-rose-200",
          icon: AlertTriangle,
        };
      default:
        return {
          label: prediction,
          badge: "bg-slate-100 text-slate-700 border-slate-200",
          icon: ShieldCheck,
        };
    }
  };

  // Recent scans preview (up to 5)
  const recentScans = [...scans].reverse().slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-900 via-emerald-800 to-slate-900 text-white p-6 sm:p-10 shadow-xl shadow-emerald-950/10">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Edge AI Diagnostics Ready</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight text-white">
              Welcome back, {user?.username || "Inspector"}
            </h1>
            <p className="mt-2 text-emerald-100/80 text-sm sm:text-base leading-relaxed">
              Monitor solar panel health, detect photovoltaic cell anomalies, and generate verified safety documentation.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/upload"
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-sm shadow-lg shadow-amber-500/20 transition active:scale-98"
            >
              <Plus className="w-4 h-4" />
              <span>Analyze New Panel</span>
            </Link>
          </div>
        </div>

        {/* Decorative background glows */}
        <div className="absolute right-0 top-0 -mt-12 -mr-12 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Top Statistical Metrics Cards */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-slate-900 tracking-tight">
            Inspection Metrics
          </h2>
          <button
            onClick={handleManualRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700 hover:text-emerald-800 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh Data</span>
          </button>
        </div>
        <DashboardCards scans={scans} loading={loading} />
      </div>

      {/* Recent Scans Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Recent Inspections
            </h3>
            <p className="text-xs text-slate-400">
              Latest AI panel predictions and condition assessments
            </p>
          </div>

          {scans.length > 0 && (
            <Link
              to="/history"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 hover:text-emerald-800 hover:underline"
            >
              <span>View All History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="py-12 text-center text-slate-400">
            <RefreshCw className="w-8 h-8 mx-auto mb-3 animate-spin text-emerald-600" />
            <p className="text-sm font-medium">Fetching inspection history...</p>
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold">Unable to fetch inspection data</p>
              <p className="text-xs mt-0.5">{error}</p>
            </div>
            <button
              onClick={handleManualRefresh}
              className="px-3 py-1.5 rounded-lg bg-rose-100 hover:bg-rose-200 text-rose-900 text-xs font-semibold"
            >
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && scans.length === 0 && (
          <div className="py-12 px-4 text-center">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <Inbox className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-slate-800">No inspections recorded yet</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-5">
              Upload your first solar panel image to run ML defect classification and generate reports.
            </p>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Start First Inspection</span>
            </Link>
          </div>
        )}

        {/* Scans Table (Desktop) / Cards (Mobile) */}
        {!loading && !error && recentScans.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  <th className="pb-3 px-2">Scan ID</th>
                  <th className="pb-3 px-3">Image Name</th>
                  <th className="pb-3 px-3">Predicted Condition</th>
                  <th className="pb-3 px-3">Confidence</th>
                  <th className="pb-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentScans.map((scan) => {
                  const badge = getConditionBadge(scan.prediction);
                  const Icon = badge.icon;
                  return (
                    <tr key={scan.id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-2 font-mono text-xs text-slate-500">
                        #{scan.id}
                      </td>
                      <td className="py-3.5 px-3 font-medium text-slate-800 text-xs truncate max-w-[200px]">
                        {scan.image_name}
                      </td>
                      <td className="py-3.5 px-3">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border ${badge.badge}`}
                        >
                          <Icon className="w-3.5 h-3.5" />
                          <span>{badge.label}</span>
                        </span>
                      </td>
                      <td className="py-3.5 px-3 font-semibold text-slate-800 text-xs">
                        {scan.confidence}
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        <button
                          onClick={() => handleDownloadReport(scan)}
                          disabled={downloadingId === scan.id}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 border border-transparent hover:border-emerald-200 text-xs font-medium transition disabled:opacity-50"
                        >
                          {downloadingId === scan.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <FileDown className="w-3.5 h-3.5" />
                          )}
                          <span>Report</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}