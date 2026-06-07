import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import client, { apiError } from '../api/client'

export default function VerifyEmail() {
  const [params] = useSearchParams()
  const [status, setStatus] = useState('verifying') // verifying | success | error
  const [message, setMessage] = useState('')
  const ran = useRef(false)

  useEffect(() => {
    if (ran.current) return // 避免 StrictMode 重複觸發消耗 token
    ran.current = true
    const token = params.get('token')
    if (!token) {
      setStatus('error')
      setMessage('缺少驗證 token')
      return
    }
    client
      .get('/auth/verify-email', { params: { token } })
      .then((res) => {
        setStatus('success')
        setMessage(res.data.message)
      })
      .catch((err) => {
        setStatus('error')
        setMessage(apiError(err, '驗證失敗'))
      })
  }, [params])

  return (
    <div className="auth-shell">
      <div className="card p-8 text-center">
        {status === 'verifying' && (
          <p className="text-slate-400 inline-flex items-center gap-2 justify-center">
            <span className="spinner" /> 驗證中…
          </p>
        )}
        {status === 'success' && (
          <>
            <div className="text-4xl mb-3">✅</div>
            <p className="text-emerald-300">{message}</p>
            <Link to="/login" className="btn-primary mt-5">
              前往登入
            </Link>
          </>
        )}
        {status === 'error' && (
          <>
            <div className="text-4xl mb-3">⚠️</div>
            <p className="text-red-300">{message}</p>
            <Link to="/login" className="link inline-block mt-5">
              返回登入
            </Link>
          </>
        )}
      </div>
    </div>
  )
}
