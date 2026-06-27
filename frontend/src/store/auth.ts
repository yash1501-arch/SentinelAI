import { create } from "zustand";
import type { User, UserLogin } from "@/types";
import * as authService from "@/services/auth";

type AuthState = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (credentials) => {
    const data = await authService.login(credentials);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    set({ user: data.user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }
      const user = await authService.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  updateProfile: async (updates) => {
    const user = await authService.updateProfile(updates);
    set({ user });
  },
}));
