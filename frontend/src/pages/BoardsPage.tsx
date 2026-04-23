/**
 * BoardsPage — list and create boards
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { boardsApi } from '@/services/api'
import type { Board } from '@/types'

function CreateBoardModal({ onClose, onCreate }: { onClose: () => void; onCreate: (b: Board) => void }) {
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) { setError('Board name is required.'); return }
    setLoading(true)
    try {
      const board = await boardsApi.create({ name: name.trim(), description: desc.trim() || undefined })
      onCreate(board)
      onClose()
    } catch {
      setError('Failed to create board. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal animate-slide-up" role="dialog" aria-modal="true" aria-labelledby="modal-create-board-title">
        <div className="modal-header">
          <h3 className="modal-title" id="modal-create-board-title">New Board</h3>
          <button className="btn btn-ghost btn-icon" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {error && <div className="auth-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

        <form className="modal-form" onSubmit={handleSubmit} id="create-board-form">
          <div className="form-group">
            <label className="form-label" htmlFor="board-name">Board Name *</label>
            <input
              id="board-name"
              type="text"
              className="form-input"
              placeholder="Q2 Sprint, Product Roadmap…"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="board-desc">Description</label>
            <textarea
              id="board-desc"
              className="form-textarea"
              placeholder="What is this board for?"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
            />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button id="create-board-submit" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating…' : 'Create Board'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export function BoardsPage() {
  const [boards, setBoards] = useState<Board[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    boardsApi.list().then(setBoards).finally(() => setLoading(false))
  }, [])

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Delete this board and all its tasks?')) return
    await boardsApi.delete(id)
    setBoards((b) => b.filter((board) => board.id !== id))
  }

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="page-header flex justify-between items-center">
        <div>
          <h1>Boards</h1>
          <p>Organize your work into boards and tasks.</p>
        </div>
        <button id="open-create-board" className="btn btn-primary" onClick={() => setShowModal(true)}>
          + New Board
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="loading-center"><div className="spinner" /></div>
      ) : boards.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">◫</div>
          <h3>No boards yet</h3>
          <p>Create your first board to start tracking tasks.</p>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            Create First Board
          </button>
        </div>
      ) : (
        <div className="boards-grid">
          {boards.map((board) => (
            <Link to={`/boards/${board.id}`} key={board.id} className="board-card">
              <div className="board-card-header">
                <h3 className="board-card-name">{board.name}</h3>
                <button
                  className="btn btn-ghost btn-icon btn-sm"
                  onClick={(e) => handleDelete(e, board.id)}
                  aria-label={`Delete board ${board.name}`}
                  style={{ color: 'var(--color-danger)', opacity: 0.7 }}
                >
                  🗑
                </button>
              </div>
              {board.description && (
                <p className="board-card-desc">{board.description}</p>
              )}
              <div className="board-card-footer">
                <span className="board-task-count">
                  ✓ {board.task_count} {board.task_count === 1 ? 'task' : 'tasks'}
                </span>
                <span className="text-sm text-muted">
                  {new Date(board.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <CreateBoardModal
          onClose={() => setShowModal(false)}
          onCreate={(b) => setBoards((prev) => [b, ...prev])}
        />
      )}
    </div>
  )
}
