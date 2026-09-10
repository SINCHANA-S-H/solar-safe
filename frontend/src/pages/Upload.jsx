import { useState } from "react";
import { useAuth } from "../context/useAuth";
import predictionService from "../services/predictionService";
import UploadCard from "../components/upload/UploadCard";
import PredictionCard from "../components/upload/PredictionCard";
import AIAnalysis from "../components/upload/AIAnalysis";
import GradCAMViewer from "../components/upload/GradCAMViewer";
import { Cpu, Sparkles, Layers, ShieldCheck } from "lucide-react";

export default function Upload() {
  const { user } = useAuth();

  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState("");
  const [error, setError] = useState(null);
  const [predictionData, setPredictionData] = useState(null);

  // Grad-CAM specific state
  const [gradCamImageUrl, setGradCamImageUrl] = useState(null);
  const [isGradCamLoading, setIsGradCamLoading] = useState(false);
  const [gradCamError, setGradCamError] = useState(null);

  // When a new image is selected or removed, wipe old analysis state
  const handleFileSelected = () => {
    setPredictionData(null);
    setGradCamImageUrl(null);
    setGradCamError(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile || !user?.email) {
      setError("Please select a solar panel image first.");
      return;
    }

    setError(null);
    setGradCamError(null);
    setGradCamImageUrl(null);
    setIsAnalyzing(true);
    setAnalysisStage("Uploading image to Solar Safe backend...");

    try {
      setTimeout(() => {
        setAnalysisStage("Running MobileNetV2 feature extraction...");
      }, 500);

      setTimeout(() => {
        setAnalysisStage("Computing class probabilities and anomaly confidence...");
      }, 1100);

      const response = await predictionService.predictImage(
        selectedFile,
        user.email
      );

      setPredictionData(response);
      setIsAnalyzing(false);

      // Trigger Grad-CAM generation with separate loading state
      setIsGradCamLoading(true);

      let gradCamCandidateUrl = null;
      if (response.gradcam_image) {
        gradCamCandidateUrl = predictionService.getGradCamUrl(response.gradcam_image);
      } else if (response.image_name) {
        const stem = response.image_name.replace(/\.[^/.]+$/, "");
        gradCamCandidateUrl = predictionService.getGradCamUrl(`/uploads/gradcam_${stem}.png`);
      }

      if (gradCamCandidateUrl) {
        const img = new Image();
        img.onload = () => {
          setGradCamImageUrl(gradCamCandidateUrl);
          setIsGradCamLoading(false);
        };
        img.onerror = () => {
          // Fallback to dedicated endpoint /gradcam/{image_name}
          if (response.image_name) {
            const fallbackUrl = predictionService.getGradCamUrl(`/gradcam/${response.image_name}`);
            const imgFallback = new Image();
            imgFallback.onload = () => {
              setGradCamImageUrl(fallbackUrl);
              setIsGradCamLoading(false);
            };
            imgFallback.onerror = () => {
              setGradCamError("AI explanation is currently unavailable.");
              setIsGradCamLoading(false);
            };
            imgFallback.src = fallbackUrl;
          } else {
            setGradCamError("AI explanation is currently unavailable.");
            setIsGradCamLoading(false);
          }
        };
        img.src = gradCamCandidateUrl;
      } else {
        setGradCamError("AI explanation is currently unavailable.");
        setIsGradCamLoading(false);
      }
    } catch (err) {
      setError(
        err.message ||
          "Failed to process image prediction. Please ensure the Solar Safe backend is running."
      );
      setIsAnalyzing(false);
    } finally {
      setAnalysisStage("");
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setPredictionData(null);
    setGradCamImageUrl(null);
    setGradCamError(null);
    setIsGradCamLoading(false);
    setError(null);
  };

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-slate-900">
            Solar PV Fault Inspection
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Analyze electroluminescence (EL) or high-res thermal module captures for defects
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 rounded-xl w-fit">
          <Cpu className="w-4 h-4 text-emerald-600" />
          <span>Model: MobileNetV2 (224×224)</span>
        </div>
      </div>

      {/* Grid: Left Upload & Controls, Right Diagnostics & Explainability */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
        {/* Left Column (5 cols on large screens) */}
        <div className="lg:col-span-5 space-y-6">
          <UploadCard
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            imagePreview={imagePreview}
            setImagePreview={setImagePreview}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
            analysisStage={analysisStage}
            error={error}
            setError={setError}
            onFileSelected={handleFileSelected}
          />

          {/* Model Specification Card */}
          <div className="bg-slate-50 rounded-2xl border border-slate-200/80 p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              Inspection Classes Supported
            </h4>
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="p-2.5 rounded-xl bg-white border border-slate-200/80">
                <span className="block font-bold text-emerald-700">Normal</span>
                <span className="text-[10px] text-slate-400">Intact Wafer</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white border border-slate-200/80">
                <span className="block font-bold text-amber-700">Hotspot</span>
                <span className="text-[10px] text-slate-400">Thermal Defect</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white border border-slate-200/80">
                <span className="block font-bold text-rose-700">Cell Crack</span>
                <span className="text-[10px] text-slate-400">Micro-Fracture</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Prediction & Technical Diagnostic (7 cols on large screens) */}
        <div className="lg:col-span-7 space-y-6">
          {predictionData ? (
            <>
              <PredictionCard
                predictionData={predictionData}
                onReset={handleReset}
              />
              <AIAnalysis predictionData={predictionData} />
              <GradCAMViewer
                gradCamImageUrl={gradCamImageUrl}
                originalImageUrl={imagePreview}
                isLoading={isGradCamLoading}
                hasAnalyzed={Boolean(predictionData)}
                error={gradCamError}
                prediction={predictionData?.prediction}
                confidence={predictionData?.confidence}
              />
            </>
          ) : (
            <div className="space-y-6">
              <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-8 sm:p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
                <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                  <Sparkles className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 tracking-tight">
                  AI Diagnostics Awaiting Input
                </h3>
                <p className="text-xs sm:text-sm text-slate-500 max-w-md mt-1.5 leading-relaxed">
                  Select a solar panel image on the left and click <strong>"Analyze Panel with AI"</strong>.
                  The system will compute class probabilities, risk assessment, and technical recommendations.
                </p>

                <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md w-full text-left text-xs text-slate-600">
                  <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>Real-time ML Confidence</span>
                  </div>
                  <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50">
                    <Cpu className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>MobileNetV2 Classification</span>
                  </div>
                </div>
              </div>

              {/* Show Grad-CAM placeholder before analysis */}
              <GradCAMViewer
                gradCamImageUrl={null}
                originalImageUrl={imagePreview}
                isLoading={false}
                hasAnalyzed={false}
                error={null}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}