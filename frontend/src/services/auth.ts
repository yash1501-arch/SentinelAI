import api from "@/lib/api"
import type { User, UserLogin, TokenResponse } from "@/types"

export async function login(credentials: UserLogin) {
  const { data } = await api.post<TokenResponse>("/auth/login", credentials)
  return data
}

export async function register(payload: Record<string, unknown>) {
  const { data } = await api.post("/auth/register", payload)
  return data
}

export async function getMe() {
  const { data } = await api.get<User>("/auth/me")
  return data
}

export async function updateProfile(updates: Partial<User>) {
  const { data } = await api.put<User>("/auth/me", updates)
  return data
}

export async function changePassword(payload: { current_password: string; new_password: string }) {
  const { data } = await api.put("/auth/change-password", payload)
  return data
}
