import { create } from "zustand";

type AuthState = {
  token: string | null;
  email: string | null;
  setAuth: (token: string, email: string) => void;
  logout: () => void;
  hydrate: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  email: null,
  setAuth: (token, email) => {
    localStorage.setItem("cv_token", token);
    set({ token, email });
  },
  logout: () => {
    localStorage.removeItem("cv_token");
    set({ token: null, email: null });
  },
  hydrate: () => {
    const token = localStorage.getItem("cv_token");
    set({ token });
  },
}));
