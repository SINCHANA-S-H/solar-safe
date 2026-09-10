import { useState, useRef } from "react";
import { UploadCloud, Image as ImageIcon, X, AlertCircle, FileCheck, RefreshCw } from "lucide-react";

export default function UploadCard({
  selectedFile,
  setSelectedFile,
  imagePreview,
  setImagePreview,
  onAnalyze,
  isAnalyzing,
  analysisStage,
  error,
  setError,
  onFileSelected,
}) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const allowedTypes = ["image/jpeg", "image/jpg", "image/png"];

  const handleFile = (file) => {
    setError(null);
    if (!file) return;

    if (!allowedTypes.includes(file.type.toLowerCase())) {
      setError("Invalid file format. Please upload a JPG or PNG image.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError("File size exceeds 15MB. Please upload a smaller solar panel image.");
      return;
    }

    if (onFileSelected) {
      onFileSelected();
    }

    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setError(null);
    if (onFileSelected) {
      onFileSelected();
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Upload Solar PV Image</h2>
          <p className="text-xs text-slate-500">
            Upload electroluminescence (EL) or thermal/visual PV panel capture
          </p>
        </div>
        {selectedFile && !isAnalyzing && (
          <button
            onClick={handleRemove}
            className="flex items-center gap-1.5 text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 px-2.5 py-1.5 rounded-lg transition"
          >
            <X className="w-3.5 h-3.5" />
            <span>Remove</span>
          </button>
        )}
      </div>

      {/* Error alert if any */}
      {error && (
        <div className="mb-4 flex items-start gap-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
          <div className="flex-1 text-xs sm:text-sm">{error}</div>
        </div>
      )}

      {/* Upload Zone / Preview Area */}
      {!imagePreview ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[280px] ${
            isDragging
              ? "border-emerald-500 bg-emerald-50/50 scale-[0.99]"
              : "border-slate-300 hover:border-emerald-500 hover:bg-slate-50/70 bg-slate-50/30"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,image/jpeg,image/png"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-4 shadow-xs">
            <UploadCloud className="w-8 h-8" />
          </div>

          <p className="text-base font-semibold text-slate-800 mb-1">
            Drag & drop solar panel image here
          </p>
          <p className="text-xs text-slate-500 mb-4 max-w-sm">
            Supported formats: <strong className="text-slate-700 font-semibold">JPG, JPEG, PNG</strong> (Max 15MB)
          </p>

          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white font-medium text-xs shadow-xs hover:bg-slate-800 transition">
            <ImageIcon className="w-3.5 h-3.5" />
            <span>Browse Files</span>
          </span>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 flex items-center justify-center max-h-[380px]">
            <img
              src={imagePreview}
              alt="Selected Solar Panel"
              className="w-full h-full object-contain max-h-[360px]"
            />
            {isAnalyzing && (
              <div className="absolute inset-0 bg-slate-900/75 backdrop-blur-xs flex flex-col items-center justify-center p-6 text-white text-center">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center mb-4">
                  <RefreshCw className="w-6 h-6 text-emerald-400 animate-spin" />
                </div>
                <h4 className="text-base font-bold tracking-tight mb-1">
                  AI Model Inspection in Progress
                </h4>
                <p className="text-xs text-emerald-300 font-medium">
                  {analysisStage || "Analyzing solar panel image..."}
                </p>
                <div className="w-48 h-1.5 bg-slate-700 rounded-full mt-4 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-amber-400 rounded-full animate-pulse-subtle w-full" />
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600">
            <div className="flex items-center gap-2 truncate max-w-full">
              <FileCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="font-semibold text-slate-800 truncate">
                {selectedFile?.name}
              </span>
              <span className="text-slate-400 shrink-0">
                ({(selectedFile?.size / 1024).toFixed(1)} KB)
              </span>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isAnalyzing}
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 underline underline-offset-2 shrink-0 disabled:opacity-50"
            >
              Change image
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <button
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white font-bold text-sm shadow-md shadow-emerald-600/25 transition active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running Inference...</span>
              </>
            ) : (
              <>
                <UploadCloud className="w-4 h-4" />
                <span>Analyze Panel with AI</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
