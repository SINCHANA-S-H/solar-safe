import api from "./api";

export const predictionService = {
  /**
   * Upload solar panel image and obtain AI fault prediction
   * POST /predict (multipart/form-data with email and image)
   */
  async predictImage(file, email, onUploadProgress = null) {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("image", file);

    const config = {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    };

    if (onUploadProgress) {
      config.onUploadProgress = onUploadProgress;
    }

    const response = await api.post("/predict", formData, config);
    return response.data;
  },

  /**
   * Helper to format full Grad-CAM URL from relative path or image name
   */
  getGradCamUrl(imageNameOrPath) {
    if (!imageNameOrPath) return null;
    if (imageNameOrPath.startsWith("http://") || imageNameOrPath.startsWith("https://")) {
      return imageNameOrPath;
    }
    const cleanPath = imageNameOrPath.startsWith("/") ? imageNameOrPath : `/uploads/${imageNameOrPath}`;
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    return `${baseUrl}${cleanPath}`;
  },

  /**
   * Dedicated endpoint to fetch Grad-CAM image as blob or directly verify existence
   * GET /gradcam/{image_name}
   */
  async fetchGradCamBlob(imageName) {
    const response = await api.get(`/gradcam/${imageName}`, {
      responseType: "blob",
    });
    return URL.createObjectURL(response.data);
  },
};

export default predictionService;
