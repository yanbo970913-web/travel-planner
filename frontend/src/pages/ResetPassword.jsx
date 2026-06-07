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
    <div className="max-w-md mx-auto mt-12 px-4">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
        <h1 className="text-2xl font-bold mb-6">重設密碼</h1>
        {!token ? (
          <p className="text-red-600 text-sm">缺少重設 token，請重新申請。</p>
        ) : done ? (
          <div className="text-sm text-green-700 bg-green-50 rounded-md p-4">
            {done}
            <div className="mt-3">
              <Link to="/login" className="text-brand-600 font-medium">
                前往登入 →
              </Link>
            </div>
          </div>
        ) : (
          <>
            {error && (
              <div className="mb-4 text-sm text-red-600 bg-red-50 rounded-md p-3">
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="password"
                required
                minLength={8}
                placeholder="新密碼（至少 8 碼）"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-brand-600 text-white py-2.5 rounded-md font-medium hover:bg-brand-700 disabled:opacity-60"
              >
                {loading ? '送出中…' : '設定新密碼'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
