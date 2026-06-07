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
    <div className="max-w-md mx-auto mt-12 px-4">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
        <h1 className="text-2xl font-bold mb-6">忘記密碼</h1>
        {done ? (
          <div className="text-sm text-green-700 bg-green-50 rounded-md p-4">
            {done}
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
                type="email"
                required
                placeholder="輸入註冊信箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-brand-600 text-white py-2.5 rounded-md font-medium hover:bg-brand-700 disabled:opacity-60"
              >
                {loading ? '寄送中…' : '寄送重設連結'}
              </button>
            </form>
          </>
        )}
        <div className="mt-4 text-sm">
          <Link to="/login" className="text-brand-600 hover:underline">
            返回登入
          </Link>
        </div>
      </div>
    </div>
  )
}
