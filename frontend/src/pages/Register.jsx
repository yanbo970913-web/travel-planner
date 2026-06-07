import { useState } from 'react'
import { Link } from 'react-router-dom'
import client, { apiError } from '../api/client'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [done, setDone] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await client.post('/auth/register', { email, password })
      setDone(res.data.message)
    } catch (err) {
      setError(apiError(err, '註冊失敗'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="card p-8">
        <h1 className="text-2xl font-bold mb-6 text-white">註冊</h1>
        {done ? (
          <div className="alert-success">
            {done}
            <div className="mt-3">
              <Link to="/login" className="link font-medium">
                前往登入 →
              </Link>
            </div>
          </div>
        ) : (
          <>
            {error && <div className="alert-error mb-4">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="email"
                required
                placeholder="電子信箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
              />
              <input
                type="password"
                required
                minLength={8}
                placeholder="密碼（至少 8 碼）"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />
              <button type="submit" disabled={loading} className="btn-primary w-full">
                {loading ? <><span className="spinner" /> 註冊中…</> : '註冊'}
              </button>
            </form>
            <p className="mt-4 text-sm text-slate-400">
              已有帳號？{' '}
              <Link to="/login" className="link">
                登入
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  )
}
