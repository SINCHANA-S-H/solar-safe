import { useState } from "react";
import {
  Eye,
  Layers,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  SplitSquareVertical,
} from "lucide-react";

export default function GradCAMViewer({
  gradCamImageUrl = null,
  originalImageUrl = null,
  isLoading = false,
  hasAnalyzed = false,
  error = null,
  prediction = null,
  confidence = null,
}) {
  const [activeTab, setActiveTab] = useState("overlay"); // "overlay", "original", "sidebyside"

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-50 text-amber-600 border border-amber-200">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900 tracking-tight flex items-center gap-2">
              Model Explainability (Grad-CAM)
              {isLoading && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 animate-pulse">
                  Computing
                </span>
              )}
              {!isLoading && gradCamImageUrl && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                  Active Heatmap
                </span>
              )}
            </h3>
            <p className="text-xs text-slate-400">
              Gradient-weighted Class Activation Mapping for visual feature validation
            </p>
          </div>
        </div>

        {/* View mode toggle buttons when Grad-CAM is available */}
        {!isLoading && gradCamImageUrl && (
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setActiveTab("overlay")}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === "overlay"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              AI Attention Overlay
            </button>
            {originalImageUrl && (
              <>
                <button
                  onClick={() => setActiveTab("original")}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    activeTab === "original"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  Original Image
                </button>
                <button
                  onClick={() => setActiveTab("sidebyside")}
                  className={`px-3 py-1.5 rounded-lg transition hidden md:inline-flex items-center gap-1 ${
                    activeTab === "sidebyside"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  <SplitSquareVertical className="w-3.5 h-3.5" />
                  Side-by-Side
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* STATE 1: During Generation */}
      {isLoading && (
        <div className="rounded-2xl border border-dashed border-amber-300 bg-amber-50/40 p-8 sm:p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center mx-auto animate-pulse">
            <Loader2 className="w-6 h-6 animate-spin text-amber-600" />
          </div>
          <h4 className="font-bold text-sm text-slate-900">
            Generating AI explanation...
          </h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
            Extracting activation gradients from MobileNetV2 final convolutional layer (<code className="bg-amber-100/70 px-1 py-0.5 rounded text-amber-900 font-mono text-[11px]">out_relu</code>) and blending class activation heatmap.
          </p>
        </div>
      )}

      {/* STATE 2: Generation Failure / Error */}
      {!isLoading && error && (
        <div className="rounded-2xl border border-dashed border-rose-200 bg-rose-50/50 p-8 text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h4 className="font-bold text-sm text-rose-900">
            AI explanation is currently unavailable.
          </h4>
          <p className="text-xs text-rose-700 max-w-md mx-auto leading-relaxed">
            The neural network completed defect classification, but the gradient heatmap generation failed or timed out.
          </p>
        </div>
      )}

      {/* STATE 3: Before Analysis */}
      {!isLoading && !error && !gradCamImageUrl && !hasAnalyzed && (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 p-8 sm:p-10 text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
            <Layers className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto">
            <h4 className="font-bold text-sm text-slate-800">
              Grad-CAM will appear after AI analysis.
            </h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Upload a solar panel image and run diagnosis to view model gradient saliency highlighting regions of interest.
            </p>
          </div>
          <div className="pt-2 flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-500">
            <span className="flex items-center gap-1 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
              <Cpu className="w-3.5 h-3.5 text-emerald-600" />
              Target Conv: out_relu (7×7×1280)
            </span>
            <span className="flex items-center gap-1 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-amber-600" />
              Jet Colormap Synthesis
            </span>
          </div>
        </div>
      )}

      {/* STATE 4: After Success - Display Grad-CAM visual output */}
      {!isLoading && !error && gradCamImageUrl && (
        <div className="space-y-4">
          {/* Active Tab: AI Attention Overlay */}
          {activeTab === "overlay" && (
            <div className="rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 p-2 shadow-inner">
              <img
                src={gradCamImageUrl}
                alt="AI Attention Overlay (Grad-CAM)"
                className="w-full h-auto object-contain max-h-[380px] rounded-xl mx-auto"
              />
            </div>
          )}

          {/* Active Tab: Original Image */}
          {activeTab === "original" && originalImageUrl && (
            <div className="rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 p-2 shadow-inner">
              <img
                src={originalImageUrl}
                alt="Original Solar PV Panel"
                className="w-full h-auto object-contain max-h-[380px] rounded-xl mx-auto"
              />
            </div>
          )}

          {/* Active Tab: Side by Side */}
          {activeTab === "sidebyside" && originalImageUrl && (
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-950 p-2 text-center">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Original Input
                </span>
                <img
                  src={originalImageUrl}
                  alt="Original Solar PV Panel"
                  className="w-full h-auto object-contain max-h-[280px] rounded-lg mx-auto"
                />
              </div>

              <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-950 p-2 text-center">
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 block mb-1">
                  Grad-CAM Attention Overlay
                </span>
                <img
                  src={gradCamImageUrl}
                  alt="AI Attention Overlay"
                  className="w-full h-auto object-contain max-h-[280px] rounded-lg mx-auto"
                />
              </div>
            </div>
          )}

          {/* Explainability Details & Legend Bar */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2 text-slate-700">
                <span className="font-bold">Focus Target:</span>
                <span className="font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  {prediction || "Class"} ({confidence ? `${confidence}%` : "Verified"})
                </span>
              </div>

              <div className="flex items-center gap-1.5 text-[11px] text-slate-500 font-mono">
                <Cpu className="w-3.5 h-3.5 text-slate-400" />
                <span>Layer: out_relu (7×7×1280)</span>
              </div>
            </div>

            {/* Jet Colormap Scale */}
            <div className="space-y-1">
              <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider text-slate-400">
                <span>Low Saliency (Background)</span>
                <span>High AI Attention (Defect Region)</span>
              </div>
              <div className="h-2 rounded-full bg-gradient-to-r from-blue-600 via-cyan-400 via-yellow-400 to-red-600 shadow-xs" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
