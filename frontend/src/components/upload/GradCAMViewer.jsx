import { Eye, Layers, Cpu, CheckCircle2, Clock } from "lucide-react";

export default function GradCAMViewer({ gradCamImageUrl = null }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-50 text-amber-600 border border-amber-200">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900 tracking-tight flex items-center gap-2">
              Model Explainability (Grad-CAM)
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                Pipeline Ready
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Gradient-weighted Class Activation Mapping for visual feature validation
            </p>
          </div>
        </div>
      </div>

      {gradCamImageUrl ? (
        <div className="rounded-xl overflow-hidden border border-slate-200">
          <img
            src={gradCamImageUrl}
            alt="Grad-CAM Activation Heatmap"
            className="w-full h-auto object-contain max-h-[300px]"
          />
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/60 p-6 sm:p-8 text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-amber-100/60 text-amber-600 flex items-center justify-center mx-auto">
            <Layers className="w-6 h-6" />
          </div>

          <div className="max-w-md mx-auto">
            <h4 className="font-bold text-sm text-slate-800">
              Explainability output will appear here when Grad-CAM is enabled.
            </h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              The MobileNetV2 convolutional backbone uses layer <code className="bg-slate-200/80 px-1 py-0.5 rounded text-slate-800 text-[11px]">out_relu</code> to compute gradient saliency maps. The offline AI pipeline is implemented in <code className="bg-slate-200/80 px-1 py-0.5 rounded text-slate-800 text-[11px]">ai/src/gradcam.py</code> and will stream live heatmaps once the backend exposes the heatmap output route.
            </p>
          </div>

          <div className="pt-2 flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-500">
            <span className="flex items-center gap-1 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
              <Cpu className="w-3.5 h-3.5 text-emerald-600" />
              Feature Layer: out_relu
            </span>
            <span className="flex items-center gap-1 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-amber-600" />
              Jet Colormap Synthesis
            </span>
            <span className="flex items-center gap-1 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              Backend Route Pending
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
