import { Scan, CheckCircle2, AlertTriangle, Activity } from "lucide-react";

export default function DashboardCards({ scans = [], loading = false }) {
  // Calculate real metrics from history
  const totalScans = scans.length;
  const normalPanels = scans.filter((s) => s.prediction === "Normal").length;
  const faultsDetected = scans.filter(
    (s) => s.prediction === "Cell_Crack" || s.prediction === "Hotspot"
  ).length;

  let averageConfidence = "0.0%";
  if (scans.length > 0) {
    const sum = scans.reduce((acc, s) => {
      // Confidence in DB is formatted as e.g. "98.42%" or float
      const val = parseFloat(String(s.confidence).replace("%", "")) || 0;
      return acc + val;
    }, 0);
    averageConfidence = `${(sum / scans.length).toFixed(1)}%`;
  }

  const cards = [
    {
      title: "Total Scans",
      value: totalScans,
      subtitle: "Lifetime panel analyses",
      icon: Scan,
      color: "from-blue-500 to-blue-600",
      iconBg: "bg-blue-50 text-blue-600",
      borderColor: "border-blue-100",
    },
    {
      title: "Normal Panels",
      value: normalPanels,
      subtitle: totalScans > 0 ? `${((normalPanels / totalScans) * 100).toFixed(0)}% of inspections` : "0% of inspections",
      icon: CheckCircle2,
      color: "from-emerald-500 to-emerald-600",
      iconBg: "bg-emerald-50 text-emerald-600",
      borderColor: "border-emerald-100",
    },
    {
      title: "Faults Detected",
      value: faultsDetected,
      subtitle: "Cell cracks & thermal hotspots",
      icon: AlertTriangle,
      color: "from-rose-500 to-rose-600",
      iconBg: "bg-rose-50 text-rose-600",
      borderColor: "border-rose-100",
    },
    {
      title: "Average Confidence",
      value: averageConfidence,
      subtitle: "Model inference precision",
      icon: Activity,
      color: "from-amber-500 to-amber-600",
      iconBg: "bg-amber-50 text-amber-600",
      borderColor: "border-amber-100",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {card.title}
              </span>
              <div className={`w-9 h-9 rounded-xl ${card.iconBg} flex items-center justify-center`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              {loading ? (
                <div className="h-8 w-16 bg-slate-200 rounded-lg animate-pulse" />
              ) : (
                <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  {card.value}
                </span>
              )}
            </div>

            <p className="text-xs text-slate-400 mt-1 font-medium">
              {card.subtitle}
            </p>
          </div>
        );
      })}
    </div>
  );
}
