import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import client, { apiError } from '../api/client'

export default function ResetPassword() {
  const [params] = useSearchParams()
  const token = params.get('token')
  const [password, setPassword] = useState('')
  const [done, setDone] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await client.post('/auth/reset-password', {
        token,
        new_password: password,
      })
      setDone(res.data.message)
    } catch (err) {
      setError(apiError(err, '重設失敗'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="card p-8">
        <h1 className="text-2xl font-bold mb-6 text-white">重設密碼</h1>
        {!token ? (
          <p className="text-red-300 text-sm">缺少重設 token，請重新申請。</p>
        ) : done ? (
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
                type="password"
                required
                minLength={8}
                placeholder="新密碼（至少 8 碼）"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />
              <button type="submit" disabled={loading} className="btn-primary w-full">
                {loading ? <><span className="spinner" /> 送出中…</> : '設定新密碼'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
