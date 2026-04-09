import { useEffect, useState } from "react";
import { AuthContext, type User } from "./AuthContext";
import { fetchMe } from "../api/auth";

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuth = !!user;

  useEffect(() => {
    const token = localStorage.getItem("authToken");

    if (!token) {
      setIsLoading(false);
      return;
    }

    fetchMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("authToken");
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const login = async (token: string) => {
    localStorage.setItem("authToken", token);

    try {
      const data = await fetchMe();
      setUser(data);
    } catch {
      localStorage.removeItem("authToken");
      throw new Error("Invalid token");
    }
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuth,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
