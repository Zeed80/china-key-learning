import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { apiFetch, jsonBody, setToken as storeToken, getToken } from "./client";
import type { TokenResponse, User } from "./types";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    let cancelled = false;
    async function loadMe() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const current = await apiFetch<User>("/auth/me");
        if (!cancelled) setUser(current);
      } catch {
        storeToken(null);
        if (!cancelled) {
          setTokenState(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void loadMe();
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function applyTokenResponse(response: TokenResponse) {
    storeToken(response.access_token);
    setTokenState(response.access_token);
    setUser(response.user);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      login: async (email, password) => {
        const response = await apiFetch<TokenResponse>("/auth/login", {
          method: "POST",
          ...jsonBody({ email, password }),
        });
        await applyTokenResponse(response);
      },
      register: async (email, password) => {
        const response = await apiFetch<TokenResponse>("/auth/register", {
          method: "POST",
          ...jsonBody({ email, password }),
        });
        await applyTokenResponse(response);
      },
      logout: () => {
        storeToken(null);
        setTokenState(null);
        setUser(null);
      },
    }),
    [loading, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
