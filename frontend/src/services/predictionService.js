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
};

export default predictionService;
