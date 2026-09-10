import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import historyService from "../services/historyService";
import reportService from "../services/reportService";
import {
  FileDown,
  RefreshCw,
  AlertTriangle,
  Flame,
  CheckCircle2,
  ShieldCheck,
  Inbox,
  Plus,
  Loader2,
  Printer,
} from "lucide-react";

export default function Reports() {
  const { user } = useAuth();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingId, setDownloadingId] = useState(null);
  const [successId, setSuccessId] = useState(null);

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
          setError(err.message || "Failed to load scan records for report generation.");
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
      setError(err.message || "Failed to load scan records for report generation.");
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePdf = async (scan) => {
    setDownloadingId(scan.id);
    setSuccessId(null);
    try {
      const blob = await reportService.generateReport(
        user.email,
        scan.prediction,
        scan.confidence
      );
      reportService.downloadPdfBlob(blob, `SolarSafe_Audit_Scan_${scan.id}.pdf`);
      setSuccessId(scan.id);
      setTimeout(() => setSuccessId(null), 4000);
    } catch (err) {
      alert(`Report generation failed: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const getBadge = (prediction) => {
    switch (prediction) {
      case "Normal":
        return {
          label: "Normal Panel",
          badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
          icon: CheckCircle2,
        };
      case "Hotspot":
        return {
          label: "Hotspot Anomaly",
          badge: "bg-amber-50 text-amber-700 border-amber-200",
          icon: Flame,
        };
      case "Cell_Crack":
        return {
          label: "Wafer Crack",
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Compliance & Inspection Reports
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Generate and export official PDF inspection summaries for maintenance crews
          </p>
        </div>

        <button
          onClick={handleManualRefresh}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-xs transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Inspections</span>
        </button>
      </div>

      {/* Info Notice Box */}
      <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-900 text-xs sm:text-sm flex items-start gap-3">
        <Printer className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-amber-900">On-Demand Report Generation</p>
          <p className="text-amber-800/90 text-xs mt-0.5 leading-relaxed">
            Reports are rendered on-demand using ReportLab on the FastAPI backend with verified inspector identity, panel filename, predicted condition, and inference confidence.
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
        {/* Loading */}
        {loading && (
          <div className="py-16 text-center text-slate-400">
            <RefreshCw className="w-8 h-8 mx-auto mb-3 animate-spin text-emerald-600" />
            <p className="text-sm font-medium">Querying eligible inspections...</p>
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
              Retry
            </button>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && scans.length === 0 && (
          <div className="py-16 px-4 text-center">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <Inbox className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-slate-800">No inspections to report</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-5">
              Complete a solar panel image analysis first to generate downloadable compliance documents.
            </p>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Analyze Panel</span>
            </Link>
          </div>
        )}

        {/* Cards Grid */}
        {!loading && !error && scans.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scans.map((scan) => {
              const badge = getBadge(scan.prediction);
              const Icon = badge.icon;
              const isGenerating = downloadingId === scan.id;
              const isSuccess = successId === scan.id;

              return (
                <div
                  key={scan.id}
                  className="rounded-xl border border-slate-200 p-5 flex flex-col justify-between hover:border-slate-300 hover:shadow-sm transition bg-slate-50/40 space-y-4"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2.5">
                      <span className="text-[11px] font-mono font-bold text-slate-400">
                        INSPECTION #{scan.id}
                      </span>
                      <span
                        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-semibold border ${badge.badge}`}
                      >
                        <Icon className="w-3 h-3" />
                        <span>{badge.label}</span>
                      </span>
                    </div>

                    <p className="text-xs font-medium text-slate-800 truncate" title={scan.image_name}>
                      File: {scan.image_name}
                    </p>

                    <div className="mt-3 flex items-center justify-between text-xs text-slate-600 border-t border-slate-200/60 pt-2.5">
                      <span>Model Confidence:</span>
                      <span className="font-mono font-bold text-slate-900">{scan.confidence}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleGeneratePdf(scan)}
                    disabled={isGenerating}
                    className={`w-full flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold transition shadow-xs ${
                      isSuccess
                        ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                        : "bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50"
                    }`}
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Generating PDF...</span>
                      </>
                    ) : isSuccess ? (
                      <>
                        <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                        <span>Report Downloaded!</span>
                      </>
                    ) : (
                      <>
                        <FileDown className="w-4 h-4" />
                        <span>Generate & Download PDF</span>
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}