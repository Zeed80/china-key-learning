import { BookOpen, ClipboardCheck, Dumbbell, LayoutDashboard, LogOut, Moon, Settings, Sun } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../api/auth";
import { useTheme } from "./ThemeProvider";

export function Layout() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">汉</span>
          <div>
            <strong>Ключи</strong>
            <span>упрощенный китайский</span>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/" end>
            <LayoutDashboard size={18} /> Обзор
          </NavLink>
          <NavLink to="/overview">
            <BookOpen size={18} /> Ключи
          </NavLink>
          <NavLink to="/training">
            <Dumbbell size={18} /> Тренировка
          </NavLink>
          <NavLink to="/exam">
            <ClipboardCheck size={18} /> Экзамен
          </NavLink>
          {user?.role === "admin" ? (
            <NavLink to="/admin">
              <Settings size={18} /> Админка
            </NavLink>
          ) : null}
        </nav>
        <div className="sidebar-footer">
          <span>{user?.email}</span>
          <button className="icon-text" onClick={toggleTheme} type="button" aria-label={theme === "dark" ? "Светлая тема" : "Темная тема"}>
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            {theme === "dark" ? "Светлая" : "Темная"}
          </button>
          <button className="icon-text" onClick={logout} type="button">
            <LogOut size={18} /> Выйти
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
