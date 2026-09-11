import { useState } from "react";
import {
  CheckCircle2,
  AlertTriangle,
  Flame,
  FileDown,
  RefreshCcw,
  Loader2,
  Percent,
} from "lucide-react";
import reportService from "../../services/reportService";
import { useAuth } from "../../context/useAuth";

export default function PredictionCard({
  predictionData,
  onReset,
  onReportSuccess,
}) {
  const { user } = useAuth();
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [reportMessage, setReportMessage] = useState(null);

  if (!predictionData) return null;

  const { prediction, confidence, probabilities, image_name } = predictionData;

  // Format prediction visual traits
  const getBadgeConfig = () => {
    switch (prediction) {
      case "Normal":
        return {
          title: "Normal (Healthy Panel)",
          description: "Photovoltaic cells appear structurally sound with no major thermal or crack anomalies detected.",
          bgColor: "bg-emerald-50 text-emerald-800 border-emerald-200",
          accentColor: "from-emerald-500 to-emerald-600",
          textColor: "text-emerald-700",
          barColor: "bg-emerald-500",
          icon: CheckCircle2,
        };
      case "Hotspot":
        return {
          title: "Thermal Hotspot Anomaly",
          description: "Localized thermal concentration detected. Higher resistance or bypass diode malfunction may cause cell overheating.",
          bgColor: "bg-amber-50 text-amber-900 border-amber-200",
          accentColor: "from-amber-500 to-amber-600",
          textColor: "text-amber-700",
          barColor: "bg-amber-500",
          icon: Flame,
        };
      case "Cell_Crack":
        return {
          title: "Cell Crack Detected",
          description: "Structural fracture or micro-crack detected within silicon wafers. Immediate inspection recommended to prevent cell isolation.",
          bgColor: "bg-rose-50 text-rose-900 border-rose-200",
          accentColor: "from-rose-500 to-rose-600",
          textColor: "text-rose-700",
          barColor: "bg-rose-500",
          icon: AlertTriangle,
        };
      default:
        return {
          title: prediction,
          description: "Prediction completed by MobileNetV2 classifier.",
          bgColor: "bg-slate-50 text-slate-800 border-slate-200",
          accentColor: "from-slate-600 to-slate-700",
          textColor: "text-slate-700",
          barColor: "bg-slate-500",
          icon: AlertTriangle,
        };
    }
  };

  const badge = getBadgeConfig();
  const Icon = badge.icon;

  const handleDownloadReport = async () => {
    if (!user?.email) return;
    setDownloadingReport(true);
    setReportMessage(null);

    try {
      const blob = await reportService.generateReport(
        user.email,
        prediction,
        `${confidence}%`
      );
      reportService.downloadPdfBlob(blob, `SolarSafe_Report_${prediction}.pdf`);
      setReportMessage({ type: "success", text: "PDF Report generated and downloaded!" });
      if (onReportSuccess) onReportSuccess();
    } catch (err) {
      setReportMessage({
        type: "error",
        text: `Report generation failed: ${err.message}`,
      });
    } finally {
      setDownloadingReport(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-6">
      {/* Header & Main Prediction Badge */}
      <div>
        <div className="flex items-center justify-between gap-4 mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Inspection Result
          </span>
          {image_name && (
            <span className="text-[11px] font-mono text-slate-400 truncate max-w-[180px]">
              ID: {image_name}
            </span>
          )}
        </div>

        <div className={`p-4 rounded-xl border ${badge.bgColor} flex items-start gap-3.5`}>
          <div className="p-2 rounded-lg bg-white/70 shadow-xs shrink-0">
            <Icon className={`w-6 h-6 ${badge.textColor}`} />
          </div>
          <div>
            <h3 className="font-bold text-base sm:text-lg tracking-tight">
              {badge.title}
            </h3>
            <p className="text-xs leading-relaxed mt-0.5 opacity-90">
              {badge.description}
            </p>
          </div>
        </div>

        {/* Prominent High-Risk Warning Alert (controlled by Settings preference) */}
        {(prediction === "Hotspot" || prediction === "Cell_Crack") &&
          localStorage.getItem("solarsafe_high_risk_alerts") !== "false" && (
            <div className="mt-3 p-3.5 rounded-xl bg-rose-600 text-white flex items-center justify-between gap-3 shadow-md animate-pulse">
              <div className="flex items-center gap-2.5 text-xs sm:text-sm font-bold">
                <AlertTriangle className="w-5 h-5 text-amber-300 shrink-0" />
                <span>CRITICAL ANOMALY DETECTED: Urgent solar array safety inspection required!</span>
              </div>
            </div>
        )}
      </div>

      {/* Confidence Score */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
            <Percent className="w-3.5 h-3.5 text-slate-400" />
            Prediction Confidence
          </span>
          <span className="text-base font-extrabold text-slate-900">
            {typeof confidence === "number" ? confidence.toFixed(2) : confidence}%
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 bg-gradient-to-r ${badge.accentColor}`}
            style={{ width: `${Math.min(100, Math.max(0, Number(confidence) || 0))}%` }}
          />
        </div>
      </div>

      {/* Class-wise Probabilities */}
      {probabilities && (
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Class Probabilities Breakdown
          </h4>
          <div className="space-y-2.5">
            {Object.entries(probabilities).map(([className, probValue]) => {
              const formattedName = className === "Cell_Crack" ? "Cell Crack" : className;
              const numericProb = typeof probValue === "number" ? probValue : parseFloat(probValue) || 0;
              const isTopClass = className === prediction;

              let barColor = "bg-slate-400";
              if (className === "Normal") barColor = "bg-emerald-500";
              if (className === "Hotspot") barColor = "bg-amber-500";
              if (className === "Cell_Crack") barColor = "bg-rose-500";

              return (
                <div key={className} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span
                      className={`font-medium ${
                        isTopClass ? "text-slate-900 font-bold" : "text-slate-600"
                      }`}
                    >
                      {formattedName}
                    </span>
                    <span
                      className={`font-semibold font-mono ${
                        isTopClass ? "text-slate-900 font-bold" : "text-slate-500"
                      }`}
                    >
                      {numericProb.toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                      style={{ width: `${Math.min(100, Math.max(0, numericProb))}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Report Feedback Message */}
      {reportMessage && (
        <div
          className={`p-3 rounded-xl text-xs ${
            reportMessage.type === "success"
              ? "bg-emerald-50 border border-emerald-200 text-emerald-800"
              : "bg-rose-50 border border-rose-200 text-rose-800"
          }`}
        >
          {reportMessage.text}
        </div>
      )}

      {/* Action Buttons */}
      <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
        <button
          onClick={handleDownloadReport}
          disabled={downloadingReport}
          className="w-full sm:flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm shadow-sm shadow-emerald-600/20 transition disabled:opacity-50"
        >
          {downloadingReport ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Generating PDF...</span>
            </>
          ) : (
            <>
              <FileDown className="w-4 h-4" />
              <span>Download PDF Report</span>
            </>
          )}
        </button>

        <button
          onClick={onReset}
          className="w-full sm:w-auto flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm transition"
        >
          <RefreshCcw className="w-4 h-4" />
          <span>New Inspection</span>
        </button>
      </div>
    </div>
  );
}
