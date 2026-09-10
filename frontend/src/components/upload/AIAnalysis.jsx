import { ShieldAlert, Info, Wrench, AlertCircle } from "lucide-react";

export default function AIAnalysis({ predictionData }) {
  if (!predictionData) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 text-center text-slate-400">
        <Info className="w-8 h-8 mx-auto mb-2 text-slate-300" />
        <p className="text-sm">Upload and analyze an image to view AI-derived technical insights.</p>
      </div>
    );
  }

  const { prediction, confidence } = predictionData;

  // Derive guidance based strictly on real prediction class
  const getAnalysisInsights = () => {
    switch (prediction) {
      case "Cell_Crack":
        return {
          condition: "Wafer Micro-Crack / Mechanical Fracture",
          severity: "Medium to High",
          riskInterpretation:
            "Cell micro-cracks can cause electrical separation of sub-regions, creating localized power reduction and potential hotspots over time. Weather exposure and thermal expansion can exacerbate wafer fractures.",
          recommendation:
            "Perform high-resolution electroluminescence (EL) imaging and IV-curve tracing. If localized resistance is elevated, consider warranty replacement of the module.",
          riskColor: "text-rose-700 bg-rose-50 border-rose-200",
        };
      case "Hotspot":
        return {
          condition: "Thermal Dissipation Anomaly (Hotspot)",
          severity: "High (Potential Fire / Degradation Risk)",
          riskInterpretation:
            "Localized thermal concentrations occur when one or more cells become reverse-biased and dissipate energy instead of producing it. Often caused by cell shadowing, cracked interconnects, or failing bypass diodes.",
          recommendation:
            "Inspect bypass diodes in junction box, verify module shading, and clean surface debris. If the hotspot persists under uniform irradiance, decommission panel to prevent backsheet browning or fire risk.",
          riskColor: "text-amber-800 bg-amber-50 border-amber-200",
        };
      case "Normal":
      default:
        return {
          condition: "Standard Photovoltaic Integrity",
          severity: "Low / Normal Operation",
          riskInterpretation:
            "No localized thermal hotspots or wafer-level cracks were identified by the MobileNetV2 neural network. The panel demonstrates uniform surface response characteristics.",
          recommendation:
            "Continue standard operational schedule. Conduct routine seasonal surface cleaning to prevent soiling losses and maximize generation yield.",
          riskColor: "text-emerald-800 bg-emerald-50 border-emerald-200",
        };
    }
  };

  const insights = getAnalysisInsights();

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <ShieldAlert className="w-5 h-5 text-emerald-600" />
        <div>
          <h3 className="font-bold text-base text-slate-900 tracking-tight">
            Technical AI Analysis & Insights
          </h3>
          <p className="text-xs text-slate-400">
            Derived from MobileNetV2 deep learning feature extraction
          </p>
        </div>
      </div>

      {/* Condition & Severity Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Detected Condition
          </span>
          <span className="text-sm font-bold text-slate-800">{insights.condition}</span>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Assessed Risk Level
          </span>
          <span className="text-sm font-bold text-slate-800">{insights.severity}</span>
        </div>
      </div>

      {/* Risk Interpretation */}
      <div className="space-y-1.5">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-slate-400" />
          Technical Interpretation
        </h4>
        <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 text-xs sm:text-sm text-slate-700 leading-relaxed">
          {insights.riskInterpretation}
        </div>
      </div>

      {/* Engineering Recommendation */}
      <div className="space-y-1.5">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Wrench className="w-3.5 h-3.5 text-slate-400" />
          Recommended Field Protocol
        </h4>
        <div className={`p-3.5 rounded-xl border text-xs sm:text-sm leading-relaxed ${insights.riskColor}`}>
          {insights.recommendation}
        </div>
      </div>

      {/* Important Disclaimer */}
      <div className="pt-2 border-t border-slate-100 flex items-start gap-2 text-[11px] text-slate-400">
        <AlertCircle className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
        <p>
          <strong>Notice:</strong> This assessment is an automated deep learning prediction ({confidence}%)
          intended for inspection triage and screening, not a substitute for certified physical on-site IEC/UL electrical safety testing.
        </p>
      </div>
    </div>
  );
}
