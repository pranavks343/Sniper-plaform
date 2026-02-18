export type AuthUser = {
  id: string;
  email: string;
  created_at: string;
};

export type AuthResponse = {
  token: string;
  user: AuthUser;
};
