/**
 * RegisterPage
 */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

export function RegisterPage() {
  const [form, setForm] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setLoading(true)
    try {
      await register({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        full_name: form.full_name.trim() || undefined,
      })
      navigate('/dashboard')
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        ?? 'Registration failed. Please try again.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card animate-slide-up">
        <div className="auth-header">
          <div className="auth-logo">✦</div>
          <h1 className="auth-title">Create account</h1>
          <p className="auth-subtitle">Start managing tasks with FlowBoard</p>
        </div>

        {error && <div className="auth-error" role="alert">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit} id="register-form" noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="reg-fullname">Full Name</label>
            <input
              id="reg-fullname"
              type="text"
              className="form-input"
              placeholder="Jane Smith"
              value={form.full_name}
              onChange={set('full_name')}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-username">Username <span style={{ color: 'var(--color-danger)' }}>*</span></label>
            <input
              id="reg-username"
              type="text"
              className="form-input"
              placeholder="jane_smith"
              value={form.username}
              onChange={set('username')}
              required
              minLength={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email <span style={{ color: 'var(--color-danger)' }}>*</span></label>
            <input
              id="reg-email"
              type="email"
              className="form-input"
              placeholder="jane@example.com"
              value={form.email}
              onChange={set('email')}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password <span style={{ color: 'var(--color-danger)' }}>*</span></label>
            <input
              id="reg-password"
              type="password"
              className="form-input"
              placeholder="Min. 8 characters"
              value={form.password}
              onChange={set('password')}
              required
              minLength={8}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">Confirm Password <span style={{ color: 'var(--color-danger)' }}>*</span></label>
            <input
              id="reg-confirm"
              type="password"
              className="form-input"
              placeholder="Repeat password"
              value={form.confirmPassword}
              onChange={set('confirmPassword')}
              required
            />
          </div>

          <button
            id="register-submit"
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={loading}
          >
            {loading ? <><span className="spinner spinner-sm" /> Creating account…</> : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login">Sign in &rarr;</Link>
        </p>
      </div>
    </div>
  )
}
