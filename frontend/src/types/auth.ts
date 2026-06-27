export type Role = {
  id: string;
  name: string;
  description: string | null;
  priority_level: string;
};

export type User = {
  id: string;
  email: string;
  username: string;
  full_name: string;
  phone: string | null;
  designation: string | null;
  badge_number: string | null;
  department: string | null;
  jurisdiction: string | null;
  is_active: boolean;
  is_superuser: boolean;
  last_login: string | null;
  preferred_language: string;
  roles: Role[];
  created_at: string;
};

export type UserCreate = {
  email: string;
  username: string;
  full_name: string;
  password: string;
  phone?: string | null;
  designation?: string | null;
  badge_number?: string | null;
  department?: string | null;
  jurisdiction?: string | null;
  preferred_language?: string;
};

export type UserUpdate = {
  full_name?: string | null;
  phone?: string | null;
  designation?: string | null;
  department?: string | null;
  jurisdiction?: string | null;
  preferred_language?: string | null;
};

export type UserLogin = {
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
};

export type TokenRefresh = {
  refresh_token: string;
};

export type PasswordChange = {
  current_password: string;
  new_password: string;
};
