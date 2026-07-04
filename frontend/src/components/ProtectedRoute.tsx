import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

import { useAuth } from "../api/auth";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token, loading } = useAuth();
  if (loading) return <div className="center-screen">Загрузка</div>;
  if (!token) return <Navigate to="/login" replace />;
  return children;
}
