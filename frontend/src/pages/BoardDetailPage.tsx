/**
 * BoardDetailPage — view and manage tasks for a single board
 */
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { boardsApi, tasksApi } from '@/services/api'
import type { Board, Task, TaskCreatePayload, TaskPriority, TaskStatus, TaskUpdatePayload } from '@/types'

const STATUS_LABELS: Record<TaskStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  done: 'Done',
}

const STATUS_COLUMNS: TaskStatus[] = ['todo', 'in_progress', 'done']

// ── Task Form Modal ───────────────────────────────────────────────────────
function TaskModal({
  boardId,
  task,
  onClose,
  onSave,
}: {
  boardId: string
  task?: Task
  onClose: () => void
  onSave: (t: Task) => void
}) {
  const [form, setForm] = useState<TaskCreatePayload & TaskUpdatePayload>({
    title: task?.title ?? '',
    description: task?.description ?? '',
    status: task?.status ?? 'todo',
    priority: task?.priority ?? 'medium',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title?.trim()) { setError('Title is required.'); return }
    setLoading(true)
    try {
      const saved = task
        ? await tasksApi.update(boardId, task.id, form)
        : await tasksApi.create(boardId, form as TaskCreatePayload)
      onSave(saved)
      onClose()
    } catch {
      setError('Failed to save task.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal animate-slide-up" role="dialog" aria-modal="true">
        <div className="modal-header">
          <h3 className="modal-title">{task ? 'Edit Task' : 'New Task'}</h3>
          <button className="btn btn-ghost btn-icon" onClick={onClose}>✕</button>
        </div>

        {error && <div className="auth-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

        <form className="modal-form" onSubmit={handleSubmit} id="task-form">
          <div className="form-group">
            <label className="form-label" htmlFor="task-title">Title *</label>
            <input id="task-title" type="text" className="form-input" placeholder="Task title…" value={form.title} onChange={set('title')} autoFocus required />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="task-desc">Description</label>
            <textarea id="task-desc" className="form-textarea" placeholder="Describe the task…" value={form.description ?? ''} onChange={set('description')} />
          </div>
          <div className="flex gap-md">
            <div className="form-group flex-1">
              <label className="form-label" htmlFor="task-status">Status</label>
              <select id="task-status" className="form-select" value={form.status} onChange={set('status')}>
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
            </div>
            <div className="form-group flex-1">
              <label className="form-label" htmlFor="task-priority">Priority</label>
              <select id="task-priority" className="form-select" value={form.priority} onChange={set('priority')}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button id="task-submit" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving…' : task ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Task Card ─────────────────────────────────────────────────────────────
function TaskCard({
  task,
  boardId,
  onEdit,
  onDelete,
  onStatusChange,
}: {
  task: Task
  boardId: string
  onEdit: () => void
  onDelete: () => void
  onStatusChange: (status: TaskStatus) => void
}) {
  const next: Record<TaskStatus, TaskStatus> = { todo: 'in_progress', in_progress: 'done', done: 'todo' }

  return (
    <div className="task-item" role="article">
      <div className="task-item-body">
        <div className="task-item-title">{task.title}</div>
        {task.description && <div className="task-item-desc">{task.description}</div>}
        <div className="task-item-meta">
          <span className={`badge badge-${task.priority}`}>{task.priority}</span>
          <button
            className={`badge badge-${task.status}`}
            style={{ cursor: 'pointer', border: 'none' }}
            onClick={() => onStatusChange(next[task.status])}
            title="Click to advance status"
          >
            {STATUS_LABELS[task.status]}
          </button>
        </div>
      </div>
      <div className="task-actions">
        <button className="btn btn-ghost btn-icon btn-sm" onClick={onEdit} aria-label="Edit task">✎</button>
        <button className="btn btn-danger btn-icon btn-sm" onClick={onDelete} aria-label="Delete task">🗑</button>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────
export function BoardDetailPage() {
  const { boardId } = useParams<{ boardId: string }>()
  const [board, setBoard] = useState<Board | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [editingTask, setEditingTask] = useState<Task | undefined>()
  const [showModal, setShowModal] = useState(false)
  const [activeFilter, setActiveFilter] = useState<TaskStatus | 'all'>('all')

  useEffect(() => {
    if (!boardId) return
    Promise.all([boardsApi.get(boardId), tasksApi.list(boardId)])
      .then(([b, t]) => { setBoard(b); setTasks(t) })
      .finally(() => setLoading(false))
  }, [boardId])

  const openCreate = () => { setEditingTask(undefined); setShowModal(true) }
  const openEdit = (t: Task) => { setEditingTask(t); setShowModal(true) }

  const handleSave = (saved: Task) => {
    setTasks((ts) => {
      const idx = ts.findIndex((t) => t.id === saved.id)
      return idx >= 0 ? ts.map((t) => (t.id === saved.id ? saved : t)) : [saved, ...ts]
    })
  }

  const handleDelete = async (taskId: string) => {
    if (!boardId || !confirm('Delete this task?')) return
    await tasksApi.delete(boardId, taskId)
    setTasks((ts) => ts.filter((t) => t.id !== taskId))
  }

  const handleStatusChange = async (task: Task, status: TaskStatus) => {
    if (!boardId) return
    const updated = await tasksApi.update(boardId, task.id, { status })
    setTasks((ts) => ts.map((t) => (t.id === task.id ? updated : t)))
  }

  const filtered = activeFilter === 'all' ? tasks : tasks.filter((t) => t.status === activeFilter)

  if (loading) return <div className="loading-center"><div className="spinner" /></div>
  if (!board) return <div className="empty-state"><h3>Board not found</h3><Link to="/boards">← Back</Link></div>

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-md" style={{ marginBottom: 'var(--spacing-xs)' }}>
          <Link to="/boards" className="btn btn-ghost btn-sm">← Boards</Link>
        </div>
        <div className="flex justify-between items-center">
          <div>
            <h1>{board.name}</h1>
            {board.description && <p>{board.description}</p>}
          </div>
          <button id="open-create-task" className="btn btn-primary" onClick={openCreate}>+ Add Task</button>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-sm" style={{ marginBottom: 'var(--spacing-lg)' }}>
        {(['all', ...STATUS_COLUMNS] as const).map((s) => (
          <button
            key={s}
            className={`btn btn-sm ${activeFilter === s ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveFilter(s)}
          >
            {s === 'all' ? `All (${tasks.length})` : `${STATUS_LABELS[s]} (${tasks.filter((t) => t.status === s).length})`}
          </button>
        ))}
      </div>

      {/* Kanban columns */}
      {activeFilter === 'all' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--spacing-lg)' }}>
          {STATUS_COLUMNS.map((col) => {
            const colTasks = tasks.filter((t) => t.status === col)
            return (
              <div key={col}>
                <div className="flex items-center gap-sm" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <span className={`badge badge-${col}`}>{STATUS_LABELS[col]}</span>
                  <span className="text-muted text-sm">{colTasks.length}</span>
                </div>
                <div className="task-list">
                  {colTasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      boardId={boardId!}
                      onEdit={() => openEdit(task)}
                      onDelete={() => handleDelete(task.id)}
                      onStatusChange={(s) => handleStatusChange(task, s)}
                    />
                  ))}
                  {colTasks.length === 0 && (
                    <div style={{ padding: 'var(--spacing-md)', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                      No tasks
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="task-list">
          {filtered.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">✓</div>
              <h3>No tasks here</h3>
              <button className="btn btn-primary" onClick={openCreate}>Add a Task</button>
            </div>
          ) : (
            filtered.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                boardId={boardId!}
                onEdit={() => openEdit(task)}
                onDelete={() => handleDelete(task.id)}
                onStatusChange={(s) => handleStatusChange(task, s)}
              />
            ))
          )}
        </div>
      )}

      {showModal && boardId && (
        <TaskModal
          boardId={boardId}
          task={editingTask}
          onClose={() => setShowModal(false)}
          onSave={handleSave}
        />
      )}
    </div>
  )
}
