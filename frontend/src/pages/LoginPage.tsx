import { Moon, Sun } from "lucide-react";
import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../api/auth";
import { useTheme } from "../components/ThemeProvider";

export function LoginPage() {
  const { token, login, register } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (token) return <Navigate to="/" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="auth-screen">
      <button className="theme-float" onClick={toggleTheme} type="button" aria-label={theme === "dark" ? "Светлая тема" : "Темная тема"}>
        {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
      </button>
      <section className="auth-panel">
        <div className="brand auth-brand">
          <span className="brand-mark">汉</span>
          <div>
            <strong>Китайские ключи</strong>
            <span>персональная тренировка</span>
          </div>
        </div>
        <div className="segmented">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">
            Вход
          </button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">
            Регистрация
          </button>
        </div>
        <form onSubmit={submit} className="form">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label>
            Пароль
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              minLength={8}
              required
            />
          </label>
          {error ? <div className="error">{error}</div> : null}
          <button disabled={pending} className="primary wide" type="submit">
            {pending ? "Подождите" : mode === "login" ? "Войти" : "Создать аккаунт"}
          </button>
        </form>
      </section>
    </main>
  );
}
