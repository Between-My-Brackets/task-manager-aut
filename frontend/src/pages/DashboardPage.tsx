/**
 * DashboardPage — animated stats overview
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboardApi } from '@/services/api'
import { useAuth } from '@/hooks/useAuth'
import type { DashboardStats } from '@/types'

interface StatCardProps {
  icon: string
  value: number
  label: string
  color: string
  bg: string
}

function StatCard({ icon, value, label, color, bg }: StatCardProps) {
  const [display, setDisplay] = useState(0)

  // Animated counter
  useEffect(() => {
    if (value === 0) return
    let current = 0
    const step = Math.ceil(value / 20)
    const timer = setInterval(() => {
      current = Math.min(current + step, value)
      setDisplay(current)
      if (current >= value) clearInterval(timer)
    }, 40)
    return () => clearInterval(timer)
  }, [value])

  return (
    <div
      className="stat-card animate-slide-up"
      style={{ '--stat-color': color, '--stat-bg': bg } as React.CSSProperties}
    >
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{display}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi
      .stats()
      .then(setStats)
      .finally(() => setLoading(false))
  }, [])

  const greeting = getGreeting()

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <h1>
          {greeting},{' '}
          <span style={{ background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-accent))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            {user?.full_name?.split(' ')[0] ?? user?.username}
          </span>{' '}
          👋
        </h1>
        <p>Here&apos;s your project overview for today.</p>
      </div>

      {/* Stats */}
      {loading ? (
        <div className="loading-center"><div className="spinner" /></div>
      ) : stats ? (
        <>
          <div className="stats-grid">
            <StatCard
              icon="◫"
              value={stats.total_boards}
              label="Total Boards"
              color="var(--color-primary)"
              bg="rgba(108,99,255,0.12)"
            />
            <StatCard
              icon="✓"
              value={stats.total_tasks}
              label="Total Tasks"
              color="var(--color-accent)"
              bg="rgba(6,214,160,0.12)"
            />
            <StatCard
              icon="○"
              value={stats.tasks_by_status.todo}
              label="To Do"
              color="var(--color-todo)"
              bg="rgba(148,163,184,0.1)"
            />
            <StatCard
              icon="◎"
              value={stats.tasks_by_status.in_progress}
              label="In Progress"
              color="var(--color-in-progress)"
              bg="rgba(108,99,255,0.12)"
            />
            <StatCard
              icon="●"
              value={stats.tasks_by_status.done}
              label="Done"
              color="var(--color-done)"
              bg="rgba(6,214,160,0.12)"
            />
          </div>

          {/* Priority Breakdown */}
          <div className="card" style={{ marginTop: 'var(--spacing-xl)' }}>
            <h3 style={{ marginBottom: 'var(--spacing-lg)' }}>Priority Breakdown</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {[
                { label: 'High', key: 'high' as const, color: 'var(--color-high)', cls: 'badge-high' },
                { label: 'Medium', key: 'medium' as const, color: 'var(--color-medium)', cls: 'badge-medium' },
                { label: 'Low', key: 'low' as const, color: 'var(--color-low)', cls: 'badge-low' },
              ].map(({ label, key, color, cls }) => {
                const count = stats.tasks_by_priority[key]
                const pct = stats.total_tasks > 0 ? (count / stats.total_tasks) * 100 : 0
                return (
                  <div key={key}>
                    <div className="flex justify-between items-center" style={{ marginBottom: 6 }}>
                      <span className={`badge ${cls}`}>{label}</span>
                      <span className="text-sm text-muted">{count} tasks</span>
                    </div>
                    <div style={{ height: 6, background: 'var(--border-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${pct}%`,
                        background: color,
                        borderRadius: 'var(--radius-full)',
                        transition: 'width 0.8s ease',
                      }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Quick action */}
          {stats.total_boards === 0 && (
            <div className="empty-state" style={{ marginTop: 'var(--spacing-xl)' }}>
              <div className="empty-state-icon">🎯</div>
              <h3>No boards yet</h3>
              <p>Create your first board to start organizing tasks.</p>
              <Link to="/boards" className="btn btn-primary">Create a Board</Link>
            </div>
          )}
        </>
      ) : null}
    </div>
  )
}

function getGreeting(): string {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}
