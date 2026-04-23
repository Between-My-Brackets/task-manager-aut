import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

export function NotFoundPage() {
  return (
    <div className="empty-state" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div className="empty-state-icon">🌌</div>
      <h3 style={{ fontSize: '1.5rem' }}>404 — Page not found</h3>
      <p>This page doesn't exist in this dimension.</p>
      <a href="/dashboard" className="btn btn-primary">Go to Dashboard</a>
    </div>
  )
}

export function RootRedirect() {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return null
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
}
