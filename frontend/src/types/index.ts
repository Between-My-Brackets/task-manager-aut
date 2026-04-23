// ── Domain Types ──────────────────────────────────────────────────────────

export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface User {
  id: string
  username: string
  email: string
  full_name?: string | null
  created_at: string
}

export interface Board {
  id: string
  name: string
  description?: string | null
  owner_id: string
  created_at: string
  task_count: number
}

export interface Task {
  id: string
  board_id: string
  title: string
  description?: string | null
  status: TaskStatus
  priority: TaskPriority
  created_at: string
  updated_at: string
}

// ── Request Payloads ──────────────────────────────────────────────────────

export interface RegisterPayload {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface BoardCreatePayload {
  name: string
  description?: string
}

export interface TaskCreatePayload {
  title: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
}

export interface TaskUpdatePayload {
  title?: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
}

// ── API Response Types ────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface DashboardStats {
  total_boards: number
  total_tasks: number
  tasks_by_status: {
    todo: number
    in_progress: number
    done: number
  }
  tasks_by_priority: {
    low: number
    medium: number
    high: number
  }
}
