import { create } from 'zustand';

type AuthState = {
  token: string | null;
  userEmail: string | null;
  setSession: (token: string, userEmail: string) => void;
  clearSession: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userEmail: null,
  setSession: (token, userEmail) => set({ token, userEmail }),
  clearSession: () => set({ token: null, userEmail: null })
}));
