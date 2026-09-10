import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import historyService from "../services/historyService";
import reportService from "../services/reportService";
import {
  Search,
  Filter,
  FileDown,
  RefreshCw,
  AlertTriangle,
  Flame,
  CheckCircle2,
  ShieldCheck,
  Inbox,
  Plus,
  Loader2,
  Image as ImageIcon,
} from "lucide-react";

export default function History() {
  const { user } = useAuth();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterClass, setFilterClass] = useState("ALL");
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
          setError(err.message || "Failed to load inspection history.");
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
      setError(err.message || "Failed to load inspection history.");
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
      alert(`Report download failed: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const getBadge = (prediction) => {
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

  // Filter & Search logic
  const filteredScans = scans.filter((scan) => {
    const matchesSearch =
      scan.image_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scan.prediction?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(scan.id).includes(searchTerm);

    const matchesFilter =
      filterClass === "ALL" || scan.prediction === filterClass;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Scan History
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Review previous solar photovoltaic panel inspections and download reports
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleManualRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-xs transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>

          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-xs transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Scan</span>
          </Link>
        </div>
      </div>

      {/* Filters & Search Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-4 flex flex-col sm:flex-row items-center gap-3 justify-between">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by image or condition..."
            className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500 transition"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs font-semibold text-slate-400 mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Class:
          </span>
          {["ALL", "Normal", "Hotspot", "Cell_Crack"].map((cls) => (
            <button
              key={cls}
              onClick={() => setFilterClass(cls)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition shrink-0 ${
                filterClass === cls
                  ? "bg-slate-900 text-white shadow-xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {cls === "ALL" ? "All Results" : cls === "Cell_Crack" ? "Cell Crack" : cls}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {/* Loading */}
        {loading && (
          <div className="py-16 text-center text-slate-400">
            <RefreshCw className="w-8 h-8 mx-auto mb-3 animate-spin text-emerald-600" />
            <p className="text-sm font-medium">Loading history records...</p>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="p-6 text-center">
            <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto mb-2" />
            <p className="font-bold text-slate-800 text-sm">{error}</p>
            <button
              onClick={handleManualRefresh}
              className="mt-3 px-4 py-1.5 rounded-xl bg-slate-900 text-white text-xs font-semibold"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredScans.length === 0 && (
          <div className="py-16 px-4 text-center">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <Inbox className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-slate-800">
              {scans.length === 0
                ? "No scans yet. Analyze your first solar panel."
                : "No matching inspection records found."}
            </h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-5">
              {scans.length === 0
                ? "Upload an image to start running AI classification and building inspection logs."
                : "Try adjusting your search query or filter tags above."}
            </p>
            {scans.length === 0 && (
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Upload Panel</span>
              </Link>
            )}
          </div>
        )}

        {/* Table View (Desktop & Tablet) */}
        {!loading && !error && filteredScans.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/50 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  <th className="py-3.5 px-4">Scan ID</th>
                  <th className="py-3.5 px-4">Image Filename</th>
                  <th className="py-3.5 px-4">Condition</th>
                  <th className="py-3.5 px-4">Confidence</th>
                  <th className="py-3.5 px-4 text-right">PDF Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredScans.map((scan) => {
                  const badge = getBadge(scan.prediction);
                  const Icon = badge.icon;
                  return (
                    <tr key={scan.id} className="hover:bg-slate-50/70 transition">
                      <td className="py-4 px-4 font-mono text-xs font-semibold text-slate-500">
                        #{scan.id}
                      </td>
                      <td className="py-4 px-4 font-medium text-slate-800 text-xs">
                        <div className="flex items-center gap-2">
                          <ImageIcon className="w-4 h-4 text-slate-400 shrink-0" />
                          <span className="truncate max-w-[220px]">{scan.image_name}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border ${badge.badge}`}
                        >
                          <Icon className="w-3.5 h-3.5" />
                          <span>{badge.label}</span>
                        </span>
                      </td>
                      <td className="py-4 px-4 font-bold font-mono text-slate-800 text-xs">
                        {scan.confidence}
                      </td>
                      <td className="py-4 px-4 text-right">
                        <button
                          onClick={() => handleDownloadReport(scan)}
                          disabled={downloadingId === scan.id}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-semibold transition disabled:opacity-50"
                        >
                          {downloadingId === scan.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <FileDown className="w-3.5 h-3.5" />
                          )}
                          <span>Download PDF</span>
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