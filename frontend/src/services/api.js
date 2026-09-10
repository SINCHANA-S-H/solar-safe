import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor: attach auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("solarsafe_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: extract helpful error message
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage;

    if (error.response) {
      // Backend returned an error response
      const data = error.response.data;
      if (typeof data === "string") {
        errorMessage = data;
      } else if (data && data.detail) {
        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          // FastAPI validation errors
          errorMessage = data.detail.map((err) => err.msg || JSON.stringify(err)).join(", ");
        } else {
          errorMessage = JSON.stringify(data.detail);
        }
      } else if (data && data.message) {
        errorMessage = data.message;
      } else {
        errorMessage = `Request failed with status code ${error.response.status}`;
      }
    } else if (error.request) {
      // Network failure / server unreachable
      errorMessage = "Cannot reach Solar Safe backend. Ensure backend is running on " + API_BASE_URL;
    } else {
      errorMessage = error.message || "An unexpected error occurred.";
    }

    const enhancedError = new Error(errorMessage);
    enhancedError.status = error.response?.status;
    enhancedError.originalError = error;
    return Promise.reject(enhancedError);
  }
);

export default api;
export { API_BASE_URL };