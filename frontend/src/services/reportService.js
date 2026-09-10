import api from "./api";

export const reportService = {
  /**
   * Request backend to generate and return a PDF report
   * POST /report?email=...&prediction=...&confidence=...
   */
  async generateReport(email, prediction, confidence) {
    const response = await api.post("/report", null, {
      params: {
        email,
        prediction,
        confidence,
      },
      responseType: "blob",
    });
    return response.data;
  },

  /**
   * Helper to trigger download of a received PDF Blob in the browser
   */
  downloadPdfBlob(blobData, filename = "SolarSafe_Panel_Report.pdf") {
    const blob = new Blob([blobData], { type: "application/pdf" });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};

export default reportService;
