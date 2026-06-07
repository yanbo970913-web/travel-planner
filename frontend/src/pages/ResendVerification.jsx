import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import client, { apiError } from '../api/client'

export default function ResendVerification() {
  const [params] = useSearchParams()
  const [email, setEmail] = useState(params.get('email') || '')
  const [done, setDone] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await client.post('/auth/resend-verification', { email })
      setDone(res.data.message)
    } catch (err) {
      setError(apiError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="card p-8">
        <h1 className="text-2xl font-bold mb-6 text-white">重寄驗證信</h1>
        {done ? (
          <div className="alert-success">{done}</div>
        ) : (
          <>
            {error && <div className="alert-error mb-4">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="email"
                required
                placeholder="輸入註冊信箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
              />
              <button type="submit" disabled={loading} className="btn-primary w-full">
                {loading ? <><span className="spinner" /> 寄送中…</> : '重新寄出驗證信'}
              </button>
            </form>
          </>
        )}
        <div className="mt-4 text-sm">
          <Link to="/login" className="link">
            返回登入
          </Link>
        </div>
      </div>
    </div>
  )
}
