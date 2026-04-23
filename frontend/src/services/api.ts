/**
 * Axios API client
 * Automatically attaches JWT from localStorage to every request.
 */
import axios from 'axios'
import type {
  Board,
  BoardCreatePayload,
  DashboardStats,
  LoginPayload,
  RegisterPayload,
  Task,
  TaskCreatePayload,
  TaskPriority,
  TaskStatus,
  TaskUpdatePayload,
  TokenResponse,
  User,
} from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ── Auth interceptor ─────────────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('flowboard_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Auth API ──────────────────────────────────────────────────────────────
export const authApi = {
  register: (payload: RegisterPayload) =>
    api.post<User>('/auth/register', payload).then((r) => r.data),

  login: (payload: LoginPayload) =>
    api.post<TokenResponse>('/auth/login', payload).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),
}

// ── Boards API ────────────────────────────────────────────────────────────
export const boardsApi = {
  list: () => api.get<Board[]>('/boards').then((r) => r.data),

  get: (id: string) => api.get<Board>(`/boards/${id}`).then((r) => r.data),

  create: (payload: BoardCreatePayload) =>
    api.post<Board>('/boards', payload).then((r) => r.data),

  delete: (id: string) => api.delete(`/boards/${id}`),
}

// ── Tasks API ─────────────────────────────────────────────────────────────
export const tasksApi = {
  list: (boardId: string, filters?: { status?: TaskStatus; priority?: TaskPriority }) =>
    api
      .get<Task[]>(`/boards/${boardId}/tasks`, { params: filters })
      .then((r) => r.data),

  get: (boardId: string, taskId: string) =>
    api.get<Task>(`/boards/${boardId}/tasks/${taskId}`).then((r) => r.data),

  create: (boardId: string, payload: TaskCreatePayload) =>
    api.post<Task>(`/boards/${boardId}/tasks`, payload).then((r) => r.data),

  update: (boardId: string, taskId: string, payload: TaskUpdatePayload) =>
    api.put<Task>(`/boards/${boardId}/tasks/${taskId}`, payload).then((r) => r.data),

  delete: (boardId: string, taskId: string) =>
    api.delete(`/boards/${boardId}/tasks/${taskId}`),
}

// ── Dashboard API ─────────────────────────────────────────────────────────
export const dashboardApi = {
  stats: () => api.get<DashboardStats>('/dashboard/stats').then((r) => r.data),
}
