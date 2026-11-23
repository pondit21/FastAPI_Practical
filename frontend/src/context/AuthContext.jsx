import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem("token")));

  // পেজ খুললে আগের টোকেন থাকলে ইউজারকে ফিরিয়ে আনা
  useEffect(() => {
    if (!localStorage.getItem("token")) return;

    api
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  // client.js থেকে আসা লগআউট সংকেত
  useEffect(() => {
    const handleLogout = () => setUser(null);
    window.addEventListener("auth:logout", handleLogout);
    return () => window.removeEventListener("auth:logout", handleLogout);
  }, []);

  const login = useCallback(async (email, password) => {
    // OAuth2 নিয়মে ফর্ম-ডাটা পাঠাতে হয়, ফিল্ডের নাম "username" (এখানে ইমেইল)
    const body = new URLSearchParams({ username: email, password });
    const { data } = await api.post("/auth/login", body);
    localStorage.setItem("token", data.access_token);

    const me = await api.get("/auth/me");
    setUser(me.data);
    return me.data;
  }, []);

  const register = useCallback(
    async (email, password) => {
      await api.post("/auth/register", { email, password });
      return login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}