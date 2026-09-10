import { useState } from "react";
import authService from "../services/authService";
import { AuthContext } from "./authContextInstance";

export function AuthProvider({ children }) {
  // Lazy initial state prevents render cascades
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem("solarsafe_token") || null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState(() => {
    try {
      const storedUser = localStorage.getItem("solarsafe_user");
      return storedUser ? JSON.parse(storedUser) : null;
    } catch {
      return null;
    }
  });

  const [loading] = useState(false);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    const accessToken = data.access_token;

    const userProfile = {
      email,
      username: email.split("@")[0],
    };

    localStorage.setItem("solarsafe_token", accessToken);
    localStorage.setItem("solarsafe_user", JSON.stringify(userProfile));

    setToken(accessToken);
    setUser(userProfile);
    return data;
  };

  const register = async (username, email, password) => {
    const data = await authService.signup(username, email, password);
    return data;
  };

  const logout = () => {
    localStorage.removeItem("solarsafe_token");
    localStorage.removeItem("solarsafe_user");
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    isAuthenticated: Boolean(token && user),
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export default AuthProvider;
