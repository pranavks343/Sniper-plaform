import { create } from 'zustand';

type UiState = {
  sidebarOpen: boolean;
  darkMode: boolean;
  toggleSidebar: () => void;
  toggleDarkMode: () => void;
  initTheme: () => void;
};

function applyTheme(dark: boolean) {
  if (typeof document === 'undefined') return;
  const html = document.documentElement;
  if (dark) {
    html.classList.add('dark');
    html.classList.remove('light');
  } else {
    html.classList.add('light');
    html.classList.remove('dark');
  }
}

export const useUiStore = create<UiState>((set, get) => ({
  sidebarOpen: true,
  darkMode: true,

  initTheme: () => {
    if (typeof window === 'undefined') return;
    const stored = localStorage.getItem('sniper-theme');
    // Default to dark if no preference stored
    const dark = stored !== null ? stored === 'dark' : true;
    applyTheme(dark);
    set({ darkMode: dark });
  },

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  toggleDarkMode: () => {
    const next = !get().darkMode;
    applyTheme(next);
    if (typeof window !== 'undefined') {
      localStorage.setItem('sniper-theme', next ? 'dark' : 'light');
    }
    set({ darkMode: next });
  },
}));
