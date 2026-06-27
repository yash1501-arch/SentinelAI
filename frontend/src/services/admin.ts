import api from "@/lib/api"

export async function getUsers() {
  const { data } = await api.get("/admin/users")
  return data
}

export async function deactivateUser(userId: string) {
  const { data } = await api.put(`/admin/users/${userId}/deactivate`)
  return data
}

export async function getAuditLogs() {
  const { data } = await api.get("/admin/audit-logs")
  return data
}

export async function getRoles() {
  const { data } = await api.get("/admin/roles")
  return data
}

export async function getSystemHealth() {
  const { data } = await api.get("/admin/system/health")
  return data
}

export type CreateUserPayload = {
  email: string
  username: string
  full_name: string
  password: string
  role: string
  department?: string
  designation?: string
  badge_number?: string
  jurisdiction?: string
}

export type UpdateUserPayload = {
  full_name?: string
  department?: string
  designation?: string
  jurisdiction?: string
  role?: string
  is_active?: boolean
}

export async function createUser(payload: CreateUserPayload) {
  const { data } = await api.post("/admin/users", payload)
  return data
}

export async function updateUser(userId: string, payload: UpdateUserPayload) {
  const { data } = await api.put(`/admin/users/${userId}`, payload)
  return data
}

export async function deleteUser(userId: string) {
  const { data } = await api.delete(`/admin/users/${userId}`)
  return data
}

export async function assignRole(userId: string, roleName: string) {
  const { data } = await api.put(`/admin/users/${userId}/role?role_name=${roleName}`)
  return data
}
