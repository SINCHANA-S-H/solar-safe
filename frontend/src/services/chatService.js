import api from "./api";

export const chatService = {
  /**
   * Send a query to the solar safety assistant
   * POST /chat?message=...
   */
  async sendMessage(message) {
    const response = await api.post("/chat", null, {
      params: { message },
    });
    return response.data;
  },
};

export default chatService;
