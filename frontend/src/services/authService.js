import api from "./api";

export const authService = {
  /**
   * Register a new user
   * POST /signup?username=...&email=...&password=...
   */
  async signup(username, email, password) {
    const response = await api.post("/signup", null, {
      params: { username, email, password },
    });
    return response.data;
  },

  /**
   * Log in an existing user
   * POST /login?email=...&password=...
   */
  async login(email, password) {
    const response = await api.post("/login", null, {
      params: { email, password },
    });
    return response.data;
  },
};

export default authService;
