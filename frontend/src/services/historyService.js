import api from "./api";

export const historyService = {
  /**
   * Fetch scan history for a user
   * GET /history?email=...
   */
  async getHistory(email) {
    const response = await api.get("/history", {
      params: { email },
    });
    return response.data;
  },
};

export default historyService;
