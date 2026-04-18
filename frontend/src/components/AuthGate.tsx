"use client";

import { useEffect, useState, type FormEvent } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

const AUTH_KEY = "pm-authenticated";

export const AuthGate = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const stored = window.localStorage.getItem(AUTH_KEY);
    setIsAuthenticated(stored === "true");
    setIsReady(true);
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username === "user" && password === "password") {
      window.localStorage.setItem(AUTH_KEY, "true");
      setIsAuthenticated(true);
      setError("");
      return;
    }
    setError("Invalid credentials.");
  };

  const handleLogout = () => {
    window.localStorage.removeItem(AUTH_KEY);
    setIsAuthenticated(false);
    setUsername("");
    setPassword("");
  };

  if (!isReady) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
          Loading
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-md rounded-[28px] border border-[var(--stroke)] bg-white/90 p-8 shadow-[var(--shadow)] backdrop-blur">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
            Project Access
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
            Sign in
          </h1>
          <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
            Use the demo credentials to access the Kanban board.
          </p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
              Username
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                placeholder="user"
                autoComplete="username"
                required
              />
            </label>
            <label className="block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
              Password
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                placeholder="password"
                autoComplete="current-password"
                required
              />
            </label>
            {error ? (
              <p className="text-sm font-semibold text-[var(--secondary-purple)]">
                {error}
              </p>
            ) : null}
            <button
              type="submit"
              className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-xs font-semibold uppercase tracking-[0.25em] text-white transition hover:brightness-110"
            >
              Sign in
            </button>
          </form>
          <div className="mt-6 rounded-2xl border border-dashed border-[var(--stroke)] px-4 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            Demo credentials: user / password
          </div>
        </div>
      </main>
    );
  }

  return (
    <div className="relative">
      <div className="z-20">
        <div className="mx-auto flex w-full max-w-[1500px] justify-end px-6 pt-4">
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-full border border-[var(--stroke)] bg-white/90 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] shadow-[var(--shadow)] transition hover:border-[var(--primary-blue)]"
          >
            Log out
          </button>
        </div>
      </div>
      <KanbanBoard />
    </div>
  );
};
