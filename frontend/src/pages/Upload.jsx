import { useState } from "react";

import UploadCard from "../components/UploadCard";
import PredictionCard from "../components/PredictionCard";
import GradCAMViewer from "../components/GradCAMViewer";
import AIAnalysis from "../components/AIAnalysis";

function Upload() {

  const [selectedImage, setSelectedImage] = useState(null);

  return (
    <>
      <UploadCard
        selectedImage={selectedImage}
        setSelectedImage={setSelectedImage}
      />

      <PredictionCard selectedImage={selectedImage} />

      <GradCAMViewer selectedImage={selectedImage} />

      <AIAnalysis />
    </>
  );
}

export default Upload;