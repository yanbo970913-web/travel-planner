import { useState } from 'react'
import { Link } from 'react-router-dom'
import client, { apiError } from '../api/client'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [done, setDone] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await client.post('/auth/forgot-password', { email })
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
        <h1 className="text-2xl font-bold mb-6 text-white">忘記密碼</h1>
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
                {loading ? <><span className="spinner" /> 寄送中…</> : '寄送重設連結'}
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
