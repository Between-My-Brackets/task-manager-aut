/**
 * DashboardPage Tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '@/pages/DashboardPage'

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: '1', username: 'alice', email: 'alice@test.com', full_name: 'Alice Smith' },
    isAuthenticated: true,
    isLoading: false,
  }),
}))

vi.mock('@/services/api', () => ({
  dashboardApi: {
    stats: vi.fn().mockResolvedValue({
      total_boards: 3,
      total_tasks: 12,
      tasks_by_status: { todo: 5, in_progress: 4, done: 3 },
      tasks_by_priority: { high: 3, medium: 6, low: 3 },
    }),
  },
}))

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders greeting with user name', async () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByText(/alice/i)).toBeInTheDocument()
    })
  })

  it('shows a loading spinner initially', async () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    // Spinner should be visible before data loads
    const spinners = document.querySelectorAll('.spinner')
    expect(spinners.length).toBeGreaterThan(0)
    
    // Wait for the async API call to resolve so React doesn't update state after the test finishes
    await waitFor(() => {
      expect(screen.getByText(/priority/i)).toBeInTheDocument()
    })
  })

  it('renders priority breakdown section', async () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByText(/priority breakdown/i)).toBeInTheDocument()
    })
  })

  it('renders high/medium/low priority badges', async () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByText(/^high$/i)).toBeInTheDocument()
      expect(screen.getByText(/^medium$/i)).toBeInTheDocument()
      expect(screen.getByText(/^low$/i)).toBeInTheDocument()
    })
  })
})
